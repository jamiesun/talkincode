-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               5.5.24 - MySQL Community Server (GPL)
-- Server OS:                    Win64
-- HeidiSQL version:             7.0.0.4160
-- Date/time:                    2012-07-06 00:38:37
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- Dumping database structure for talkincode_db1
DROP DATABASE IF EXISTS `talkincode_db1`;
CREATE DATABASE IF NOT EXISTS `talkincode_db1` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `talkincode_db1`;


-- Dumping structure for table talkincode_db1.authkeys
DROP TABLE IF EXISTS `authkeys`;
CREATE TABLE IF NOT EXISTS `authkeys` (
  `authkey` varchar(128) NOT NULL,
  `consumer` varchar(255) NOT NULL,
  `description` varchar(1024) DEFAULT NULL,
  `hits` int(11) NOT NULL DEFAULT '0',
  `create_time` varchar(19) DEFAULT NULL,
  PRIMARY KEY (`authkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.categorys
DROP TABLE IF EXISTS `categorys`;
CREATE TABLE IF NOT EXISTS `categorys` (
  `id` int(10) NOT NULL,
  `parent` int(10) NOT NULL,
  `name` varchar(128) NOT NULL,
  `nicename` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  KEY `parent` (`parent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.codes
DROP TABLE IF EXISTS `codes`;
CREATE TABLE IF NOT EXISTS `codes` (
  `id` varchar(32) NOT NULL,
  `title` varchar(512) DEFAULT NULL,
  `auther` varchar(128) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `content` text,
  `hits` int(11) DEFAULT '0',
  `authkey` varchar(128) NOT NULL,
  `lang` varchar(32) DEFAULT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `create_time` varchar(19) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.comments
DROP TABLE IF EXISTS `comments`;
CREATE TABLE IF NOT EXISTS `comments` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `parent` int(10) NOT NULL DEFAULT '0',
  `postid` int(11) NOT NULL,
  `content` text NOT NULL,
  `author` varchar(64) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `url` varchar(128) DEFAULT NULL,
  `ip` varchar(128) DEFAULT NULL,
  `agent` varchar(128) DEFAULT NULL,
  `status` int(1) NOT NULL,
  `created` varchar(19) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.postmeta
DROP TABLE IF EXISTS `postmeta`;
CREATE TABLE IF NOT EXISTS `postmeta` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `userid` int(10) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.posts
DROP TABLE IF EXISTS `posts`;
CREATE TABLE IF NOT EXISTS `posts` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `userid` int(10) NOT NULL,
  `title` varchar(255) NOT NULL,
  `category` varchar(64) NOT NULL,
  `description` varchar(1024) DEFAULT NULL,
  `content` text NOT NULL,
  `status` int(2) NOT NULL,
  `publish` varchar(16) DEFAULT NULL,
  `created` varchar(19) NOT NULL,
  `modified` varchar(19) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `userid` (`userid`),
  KEY `category` (`category`),
  KEY `title` (`title`),
  KEY `created` (`created`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.usermeta
DROP TABLE IF EXISTS `usermeta`;
CREATE TABLE IF NOT EXISTS `usermeta` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `userid` int(10) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.users
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `nicename` varchar(64) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `url` varchar(128) DEFAULT NULL,
  `created` varchar(19) NOT NULL,
  `status` int(2) NOT NULL DEFAULT '0',
  `authkey` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
