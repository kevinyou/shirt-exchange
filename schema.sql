CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY,
    user_name TEXT,
    user_password TEXT,
    user_email TEXT,
    user_contact TEXT
);

CREATE TABLE IF NOT EXISTS offer (
    offer_id INTEGER PRIMARY KEY,
    offer_have INTEGER,
    offer_want INTEGER,
    offer_user INTEGER,
    status INTEGER,
    FOREIGN KEY(offer_user) REFERENCES user(user_id),
    FOREIGN KEY(offer_have) REFERENCES shirt(shirt_id),
    FOREIGN KEY(offer_want) REFERENCES shirt(shirt_id)
);

CREATE TABLE IF NOT EXISTS shirt (
    shirt_id INTEGER PRIMARY KEY,
    shirt_description TEXT,
    shirt_company TEXT,
    shirt_color TEXT,
    shirt_size TEXT,
    shirt_rarity INTEGER
);

CREATE TABLE IF NOT EXISTS message (
    message_id INTEGER PRIMARY_KEY,
    message_content TEXT
);
