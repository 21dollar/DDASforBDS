if not exists (SELECT * from sys.databases 
            where name = 'DDASforBDS')
    create DATABASE DDASforBDS
go

use DDASforBDS
go


IF (EXISTS (SELECT * 
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = 'DBIT'))
    DROP TABLE DBIT
go


CREATE TABLE DBIT
(
    R INT NOT NULL PRIMARY KEY,
    L INT NOT NULL,
    V INT NOT NULL,
    T varchar(255) NOT NULL,
);
GO




