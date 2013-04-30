-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               5.6.11 - MySQL Community Server (GPL)
-- Server OS:                    Win32
-- HeidiSQL version:             7.0.0.4160
-- Date/time:                    2013-04-30 13:22:59
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
  `status` int(1) DEFAULT '1',
  PRIMARY KEY (`authkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.category
DROP TABLE IF EXISTS `category`;
CREATE TABLE IF NOT EXISTS `category` (
  `id` varchar(32) NOT NULL,
  `parent` varchar(32) NOT NULL,
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
  `parent` varchar(32) DEFAULT NULL,
  `title` varchar(512) DEFAULT NULL,
  `author` varchar(128) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `content` text,
  `authkey` varchar(128) DEFAULT NULL,
  `lang` varchar(32) DEFAULT NULL,
  `filename` varchar(255) DEFAULT NULL,
  `hits` int(11) DEFAULT '0',
  `recs` int(11) DEFAULT '0',
  `create_time` varchar(32) DEFAULT NULL,
  `via` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.comments
DROP TABLE IF EXISTS `comments`;
CREATE TABLE IF NOT EXISTS `comments` (
  `id` varchar(32) NOT NULL,
  `postid` varchar(32) NOT NULL,
  `content` text NOT NULL,
  `author` varchar(64) DEFAULT NULL,
  `userid` varchar(32) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `url` varchar(128) DEFAULT NULL,
  `ip` varchar(128) DEFAULT NULL,
  `agent` varchar(128) DEFAULT NULL,
  `status` int(1) NOT NULL,
  `created` varchar(32) NOT NULL,
  `via` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.groups
DROP TABLE IF EXISTS `groups`;
CREATE TABLE IF NOT EXISTS `groups` (
  `id` int(4) NOT NULL,
  `name` varchar(32) NOT NULL DEFAULT '',
  `description` text,
  `guid` varchar(32) NOT NULL,
  `posts` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.langs
DROP TABLE IF EXISTS `langs`;
CREATE TABLE IF NOT EXISTS `langs` (
  `id` int(4) NOT NULL,
  `name` varchar(32) NOT NULL DEFAULT '',
  `ext` varchar(16) DEFAULT NULL,
  `hits` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.postmeta
DROP TABLE IF EXISTS `postmeta`;
CREATE TABLE IF NOT EXISTS `postmeta` (
  `id` varchar(32) NOT NULL,
  `postid` varchar(32) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.posts
DROP TABLE IF EXISTS `posts`;
CREATE TABLE IF NOT EXISTS `posts` (
  `id` varchar(32) NOT NULL,
  `userid` varchar(32) NOT NULL,
  `groupid` varchar(32) DEFAULT NULL,
  `codeid` varchar(32) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `description` varchar(1024) DEFAULT NULL,
  `content` text NOT NULL,
  `status` int(1) NOT NULL DEFAULT '1',
  `hits` int(10) NOT NULL DEFAULT '0',
  `recs` int(10) NOT NULL DEFAULT '0',
  `created` varchar(32) NOT NULL,
  `modified` varchar(32) NOT NULL,
  `via` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created` (`created`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.projects
DROP TABLE IF EXISTS `projects`;
CREATE TABLE IF NOT EXISTS `projects` (
  `id` varchar(32) NOT NULL,
  `image` varchar(225) DEFAULT NULL,
  `name` varchar(64) NOT NULL,
  `tags` varchar(255) DEFAULT NULL,
  `description` text,
  `owner` varchar(64) NOT NULL,
  `license` varchar(64) DEFAULT NULL,
  `homepage` varchar(128) NOT NULL,
  `docpage` varchar(128) DEFAULT NULL,
  `download` varchar(128) DEFAULT NULL,
  `hits` int(10) NOT NULL DEFAULT '0',
  `recs` int(10) NOT NULL DEFAULT '0',
  `lang` varchar(64) NOT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `created` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.settings
DROP TABLE IF EXISTS `settings`;
CREATE TABLE IF NOT EXISTS `settings` (
  `key` varchar(255) NOT NULL,
  `value` text,
  `desc` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.tags
DROP TABLE IF EXISTS `tags`;
CREATE TABLE IF NOT EXISTS `tags` (
  `id` varchar(32) NOT NULL,
  `name` varchar(64) NOT NULL,
  `desc` text NOT NULL,
  `hits` int(10) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.usermeta
DROP TABLE IF EXISTS `usermeta`;
CREATE TABLE IF NOT EXISTS `usermeta` (
  `id` varchar(32) NOT NULL,
  `userid` varchar(32) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.


-- Dumping structure for table talkincode_db1.users
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` varchar(32) NOT NULL,
  `username` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `nicename` varchar(64) DEFAULT NULL,
  `email` varchar(128) DEFAULT NULL,
  `url` varchar(128) DEFAULT NULL,
  `created` varchar(19) NOT NULL,
  `lastlogin` varchar(19) NOT NULL,
  `status` int(2) NOT NULL DEFAULT '0',
  `authkey` varchar(128) DEFAULT NULL,
  `role` int(1) unsigned zerofill DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Data exporting was unselected.
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
