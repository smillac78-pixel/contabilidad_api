-- Función que se ejecuta cuando un usuario se registra en Supabase Auth
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  new_user_id UUID;
  new_family_id UUID;
  user_name TEXT;
BEGIN
  -- Extraer nombre del metadata, si no usar parte del email
  user_name := COALESCE(
    NEW.raw_user_meta_data->>'name',
    split_part(NEW.email, '@', 1)
  );

  -- 1. Insertar usuario sin family_id aún
  INSERT INTO public.users (auth_id, email, name, is_active)
  VALUES (NEW.id, NEW.email, user_name, true)
  RETURNING id INTO new_user_id;

  -- 2. Crear familia
  INSERT INTO public.families (name, owner_id)
  VALUES (user_name || '''s family', new_user_id)
  RETURNING id INTO new_family_id;

  -- 3. Vincular usuario a su familia
  UPDATE public.users
  SET family_id = new_family_id
  WHERE id = new_user_id;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger sobre auth.users
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Categorías del sistema por defecto para cada familia nueva
CREATE OR REPLACE FUNCTION public.handle_new_family()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.categories (family_id, name, icon, color, is_system) VALUES
    (NEW.id, 'Hipoteca / Alquiler', '🏠', '#6366f1', true),
    (NEW.id, 'Electricidad',        '⚡', '#f59e0b', true),
    (NEW.id, 'Agua',                '💧', '#3b82f6', true),
    (NEW.id, 'Gas',                 '🔥', '#ef4444', true),
    (NEW.id, 'Teléfono / Internet', '📱', '#8b5cf6', true),
    (NEW.id, 'Supermercado',        '🛒', '#10b981', true),
    (NEW.id, 'Transporte',          '🚗', '#f97316', true),
    (NEW.id, 'Seguros',             '🛡️', '#64748b', true),
    (NEW.id, 'Salud',               '💊', '#ec4899', true),
    (NEW.id, 'Ocio',                '🎬', '#14b8a6', true),
    (NEW.id, 'Educación',           '📚', '#a855f7', true),
    (NEW.id, 'Otros',               '📦', '#94a3b8', true);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_family_created
  AFTER INSERT ON public.families
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_family();

-- Insertar categorías para la familia que ya existe (pepito)
INSERT INTO public.categories (family_id, name, icon, color, is_system) VALUES
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Hipoteca / Alquiler', '🏠', '#6366f1', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Electricidad',        '⚡', '#f59e0b', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Agua',                '💧', '#3b82f6', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Gas',                 '🔥', '#ef4444', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Teléfono / Internet', '📱', '#8b5cf6', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Supermercado',        '🛒', '#10b981', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Transporte',          '🚗', '#f97316', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Seguros',             '🛡️', '#64748b', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Salud',               '💊', '#ec4899', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Ocio',                '🎬', '#14b8a6', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Educación',           '📚', '#a855f7', true),
  ('b29951eb-ae7c-4df0-9460-9f68ce73d80b', 'Otros',               '📦', '#94a3b8', true)
ON CONFLICT (family_id, name) DO NOTHING;
