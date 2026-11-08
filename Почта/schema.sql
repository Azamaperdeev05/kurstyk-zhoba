-- «Пошта» ішкі жүйесі (13-нұсқа). Дерекқор мен кестелерді құру.
-- Назар аударыңыз: Pochta дерекқоры бұрыннан бар болса, ол жойылып, қайта құрылады.
USE master;
GO
IF DB_ID('Pochta') IS NOT NULL
BEGIN
    ALTER DATABASE Pochta SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Pochta;
END
GO
CREATE DATABASE Pochta;
GO
USE Pochta;
GO

CREATE TABLE Елдер (
    Ел_коды INT IDENTITY PRIMARY KEY,
    Атауы   NVARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Басылым_тілі (
    Тіл_коды INT IDENTITY PRIMARY KEY,
    Атауы    NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Жеткізу_түрі (
    Жеткізу_түрі_коды INT IDENTITY PRIMARY KEY,
    Атауы             NVARCHAR(50) NOT NULL UNIQUE  -- пошта бөлімшесі, пошта жәшігі
);

CREATE TABLE Басылым_түрі (
    Басылым_түрі_коды INT IDENTITY PRIMARY KEY,
    Атауы             NVARCHAR(50) NOT NULL UNIQUE  -- газет, журнал
);

CREATE TABLE Пошта_бөлімшесі (
    Бөлімше_коды INT IDENTITY PRIMARY KEY,
    Атауы        NVARCHAR(100) NOT NULL,
    Мекенжай     NVARCHAR(200) NOT NULL,
    Телефон      NVARCHAR(20)
);

CREATE TABLE Қызметкерлер (
    Қызметкер_коды INT IDENTITY PRIMARY KEY,
    Аты_жөні       NVARCHAR(100) NOT NULL,
    Бөлімше_коды   INT NOT NULL REFERENCES Пошта_бөлімшесі(Бөлімше_коды)
);

CREATE TABLE Жазылушы (
    Жазылушы_коды     INT IDENTITY PRIMARY KEY,
    Аты_жөні_атауы    NVARCHAR(150) NOT NULL,
    Заңды_тұлға       BIT NOT NULL DEFAULT 0,       -- 0 = жеке тұлға, 1 = заңды тұлға
    Мекенжай          NVARCHAR(200) NOT NULL,
    Телефон           NVARCHAR(20),
    Бөлімше_коды      INT NOT NULL REFERENCES Пошта_бөлімшесі(Бөлімше_коды),
    Жеңілдік_пайызы   DECIMAL(5,2) NOT NULL DEFAULT 0 CHECK (Жеңілдік_пайызы BETWEEN 0 AND 100),
    Жеткізу_түрі_коды INT NOT NULL REFERENCES Жеткізу_түрі(Жеткізу_түрі_коды)
);

CREATE TABLE Басылым (
    Басылым_индексі   INT PRIMARY KEY,               -- жазылу индексі
    Басылым_түрі_коды INT NOT NULL REFERENCES Басылым_түрі(Басылым_түрі_коды),
    Атауы             NVARCHAR(150) NOT NULL,
    Айлық_бағасы      DECIMAL(10,2) NOT NULL CHECK (Айлық_бағасы >= 0),
    Ел_коды           INT NOT NULL REFERENCES Елдер(Ел_коды),
    Тіл_коды          INT NOT NULL REFERENCES Басылым_тілі(Тіл_коды),
    Жалпы_саны        INT NOT NULL CHECK (Жалпы_саны >= 0),
    Қолжетімді_саны   INT NOT NULL,
    CHECK (Қолжетімді_саны BETWEEN 0 AND Жалпы_саны)
);

CREATE TABLE Жазылым (
    Жазылым_коды    INT IDENTITY PRIMARY KEY,
    Жазылушы_коды   INT NOT NULL REFERENCES Жазылушы(Жазылушы_коды),
    Басылым_индексі INT NOT NULL REFERENCES Басылым(Басылым_индексі),
    Жазылу_күні     DATE NOT NULL,
    Жазылу_мерзімі  INT NOT NULL CHECK (Жазылу_мерзімі BETWEEN 1 AND 12),  -- айлармен
    Қызметкер_коды  INT NOT NULL REFERENCES Қызметкерлер(Қызметкер_коды)
);

CREATE TABLE Төлем (
    Төлем_коды     INT IDENTITY PRIMARY KEY,
    Жазылушы_коды  INT NOT NULL REFERENCES Жазылушы(Жазылушы_коды),
    Күні           DATE NOT NULL,
    Сомасы         DECIMAL(10,2) NOT NULL CHECK (Сомасы > 0),
    Қызметкер_коды INT NOT NULL REFERENCES Қызметкерлер(Қызметкер_коды)
);
GO
