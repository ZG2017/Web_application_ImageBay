create database Test;
use Test;
CREATE TABLE userInfo (
	userName varchar(30) NOT NULL UNIQUE,
    userEmail varchar(255) NOT NULL UNIQUE,
    userPwd varchar(255) NOT NULL,
    userSalt varchar(255) NOT NULL,
    PRIMARY KEY (userName)
);

CREATE TABLE user2Images (
    userName varchar(30) NOT NULL,
    Thumbnail varchar(500) NOT NULL,
    original varchar(500) NOT NULL,
    trans_a varchar(500) NOT NULL,
    trans_b varchar(500) NOT NULL,
    trans_c varchar(500) NOT NULL,
    PRIMARY KEY (userName,Thumbnail),
    FOREIGN KEY (userName) REFERENCES userInfo(userName)
);




