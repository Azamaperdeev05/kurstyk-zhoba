-- «Кітапхана» ішкі жүйесі (10-нұсқа). Дерекқор мен кестелерді құру.
-- Назар аударыңыз: Biblioteka дерекқоры бұрыннан бар болса, ол жойылып, қайта құрылады.
USE master;
GO
IF DB_ID('Biblioteka') IS NOT NULL
BEGIN
    ALTER DATABASE Biblioteka SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Biblioteka;
END
GO
CREATE DATABASE Biblioteka;
GO
USE Biblioteka;
GO

CREATE TABLE Жіктеуіш (
    Жіктеуіш_бөлімі NVARCHAR(10) PRIMARY KEY,   -- мысалы, 84 = көркем әдебиет (ББК)
    Атауы           NVARCHAR(100) NOT NULL
);

CREATE TABLE Баспалар (
    Баспа_коды INT IDENTITY PRIMARY KEY,
    Атауы      NVARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Кітаптар (
    Кітап_коды      INT IDENTITY PRIMARY KEY,
    Атауы           NVARCHAR(200) NOT NULL,
    Баспа_коды      INT NOT NULL REFERENCES Баспалар(Баспа_коды),
    Шыққан_жылы     INT CHECK (Шыққан_жылы BETWEEN 1500 AND 2100),
    Жіктеуіш_бөлімі NVARCHAR(10) NOT NULL REFERENCES Жіктеуіш(Жіктеуіш_бөлімі)
);

CREATE TABLE Автор_аты_жөні (
    Автор_коды INT IDENTITY PRIMARY KEY,
    Аты_жөні   NVARCHAR(100) NOT NULL
);

CREATE TABLE Авторлар (
    Кітап_коды INT NOT NULL REFERENCES Кітаптар(Кітап_коды),
    Автор_коды INT NOT NULL REFERENCES Автор_аты_жөні(Автор_коды),
    PRIMARY KEY (Кітап_коды, Автор_коды)
);

CREATE TABLE Сақтау_орындары (
    Сөре_коды       INT IDENTITY PRIMARY KEY,
    Атауы           NVARCHAR(50) NOT NULL,
    Орналасқан_жері NVARCHAR(100) NOT NULL
);

CREATE TABLE Қор (
    Кітап_коды      INT PRIMARY KEY REFERENCES Кітаптар(Кітап_коды),
    Кепілдік_құны   DECIMAL(10,2) NOT NULL CHECK (Кепілдік_құны >= 0),
    Жалпы_саны      INT NOT NULL CHECK (Жалпы_саны >= 0),
    Қолжетімді_саны INT NOT NULL,
    Сөре_коды       INT NOT NULL REFERENCES Сақтау_орындары(Сөре_коды),
    CHECK (Қолжетімді_саны BETWEEN 0 AND Жалпы_саны)
);

CREATE TABLE Оқырмандар (
    Оқырман_коды    INT IDENTITY PRIMARY KEY,
    Аты_жөні        NVARCHAR(100) NOT NULL,
    Мекенжай        NVARCHAR(200),
    Телефон         NVARCHAR(20),
    Туған_күні      DATE NOT NULL,
    Жынысы          NCHAR(1) NOT NULL CHECK (Жынысы IN (N'Е', N'Ә')),   -- Е = ер, Ә = әйел
    Жұмыс_оқу_орны  NVARCHAR(150),
    Мамандығы       NVARCHAR(100)
);

CREATE TABLE Кітапханашылар (
    Кітапханашы_коды INT IDENTITY PRIMARY KEY,
    Аты_жөні         NVARCHAR(100) NOT NULL
);

CREATE TABLE Қозғалыс (
    Операция_коды    INT IDENTITY PRIMARY KEY,
    Кітап_коды       INT NOT NULL REFERENCES Кітаптар(Кітап_коды),
    Оқырман_коды     INT NOT NULL REFERENCES Оқырмандар(Оқырман_коды),
    Берілген_күні    DATE NOT NULL,
    Мерзімі_күн      INT NOT NULL CHECK (Мерзімі_күн > 0),   -- кітап неше күнге берілді
    Қайтарылған_күні DATE NULL,                            -- NULL = кітап әлі оқырманда
    Кітапханашы_коды INT NOT NULL REFERENCES Кітапханашылар(Кітапханашы_коды),
    CHECK (Қайтарылған_күні IS NULL OR Қайтарылған_күні >= Берілген_күні)
);

CREATE TABLE Айыппұл (
    Айыппұл_коды     INT IDENTITY PRIMARY KEY,
    Күні             DATE NOT NULL,
    Оқырман_коды     INT NOT NULL REFERENCES Оқырмандар(Оқырман_коды),
    Айыппұл_сомасы   DECIMAL(10,2) NOT NULL CHECK (Айыппұл_сомасы > 0),
    Кітапханашы_коды INT NOT NULL REFERENCES Кітапханашылар(Кітапханашы_коды)
);
GO
