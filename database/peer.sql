PRAGMA foreign_keys = ON;

CREATE TABLE Files (
	file_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	torrent_id INTEGER NOT NULL,
	file_name TEXT NOT NULL,
	total_pieces INTEGER NOT NULL,
	--
	UNIQUE(file_id, torrent_id),
	--
	CHECK (length(file_name) > 0),
	CHECK (total_pieces > 0)
);

CREATE TABLE Pieces (
	file_id INTEGER REFERENCES Files(file_id) ON DELETE CASCADE,
	piece_id INTEGER NOT NULL,
	local_path TEXT NOT NULL
);

CREATE TRIGGER befo_insert BEFORE INSERT ON Pieces
BEGIN
SELECT CASE
WHEN ((SELECT total_pieces FROM Files WHERE Files.file_id = NEW.file_id ) <= NEW.piece_id)
THEN RAISE(ABORT, 'New piece id >= file total pieces')
END;
END;

CREATE TRIGGER befo_update BEFORE UPDATE ON Pieces
BEGIN
SELECT CASE
WHEN ((SELECT total_pieces FROM Files WHERE Files.file_id = NEW.file_id ) <= NEW.piece_id)
THEN RAISE(ABORT, 'New piece id >= file total pieces')
END;
END;