CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE families (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name       VARCHAR(255) NOT NULL,
    owner_id   UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id    UUID UNIQUE NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    name       VARCHAR(255) NOT NULL,
    family_id  UUID REFERENCES families(id) ON DELETE SET NULL,
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE families
    ADD CONSTRAINT fk_families_owner
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT;

CREATE TABLE categories (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id  UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    name       VARCHAR(100) NOT NULL,
    icon       VARCHAR(50),
    color      CHAR(7),
    is_system  BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(family_id, name)
);

CREATE TABLE expenses (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id            UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    category_id          UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    created_by           UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    amount               NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    currency             CHAR(3) NOT NULL DEFAULT 'EUR',
    description          VARCHAR(500) NOT NULL,
    expense_date         DATE NOT NULL,
    is_recurring         BOOLEAN DEFAULT FALSE,
    recurring_expense_id UUID,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_expenses_family_date ON expenses(family_id, expense_date DESC);
CREATE INDEX idx_expenses_category    ON expenses(category_id);

CREATE TABLE recurring_expenses (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id     UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    category_id   UUID NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    created_by    UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    amount        NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    currency      CHAR(3) NOT NULL DEFAULT 'EUR',
    description   VARCHAR(500) NOT NULL,
    period        VARCHAR(20) NOT NULL CHECK (period IN ('weekly','monthly','yearly')),
    start_date    DATE NOT NULL,
    end_date      DATE,
    next_due_date DATE NOT NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_recurring_due    ON recurring_expenses(next_due_date) WHERE is_active = TRUE;
CREATE INDEX idx_recurring_family ON recurring_expenses(family_id);

CREATE TABLE budgets (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id   UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    amount      NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    currency    CHAR(3) NOT NULL DEFAULT 'EUR',
    period      VARCHAR(20) NOT NULL CHECK (period IN ('weekly','monthly','yearly')),
    year        SMALLINT NOT NULL,
    month       SMALLINT CHECK (month BETWEEN 1 AND 12),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(family_id, category_id, year, month)
);

CREATE INDEX idx_budgets_family_period ON budgets(family_id, year, month);
