-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: kcc_chatbot
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `kcc_chatbot`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `kcc_chatbot` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `kcc_chatbot`;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add info',6,'add_info'),(22,'Can change info',6,'change_info'),(23,'Can delete info',6,'delete_info'),(24,'Can view info',6,'view_info'),(25,'Can add user',7,'add_user'),(26,'Can change user',7,'change_user'),(27,'Can delete user',7,'delete_user'),(28,'Can view user',7,'view_user'),(29,'Can add conversation',8,'add_conversation'),(30,'Can change conversation',8,'change_conversation'),(31,'Can delete conversation',8,'delete_conversation'),(32,'Can view conversation',8,'view_conversation'),(33,'Can add message',9,'add_message'),(34,'Can change message',9,'change_message'),(35,'Can delete message',9,'delete_message'),(36,'Can view message',9,'view_message'),(37,'Can add user',10,'add_user'),(38,'Can change user',10,'change_user'),(39,'Can delete user',10,'delete_user'),(40,'Can view user',10,'view_user'),(41,'Can add knowledge category',11,'add_knowledgecategory'),(42,'Can change knowledge category',11,'change_knowledgecategory'),(43,'Can delete knowledge category',11,'delete_knowledgecategory'),(44,'Can view knowledge category',11,'view_knowledgecategory'),(45,'Can add knowledge item',12,'add_knowledgeitem'),(46,'Can change knowledge item',12,'change_knowledgeitem'),(47,'Can delete knowledge item',12,'delete_knowledgeitem'),(48,'Can view knowledge item',12,'view_knowledgeitem');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `email` varchar(254) NOT NULL,
  `middle_name` varchar(100) NOT NULL,
  `birthday` date DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `is_permanently_deactivated` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$720000$enKzRw9eEKTzuFUKBU31Vx$TfrMBDANY1pDf1GXm8Fsq/a+yJs1rs7tEohiSPV4Z1w=','2026-10-18 14:40:09.674579',1,'admin','','',1,1,'2026-10-08 16:25:02.510574','admin@admin.com','','2005-03-22','2026-10-08 16:25:03.205923',0),(28,'pbkdf2_sha256$720000$XXeV3fsvJiIu4CzIKFyfLP$EgaunZA8XOy1shnb4+pli9qb7yfKChixrxJ6PJfJzM4=','2026-10-18 14:41:56.138765',0,'gheanmamaw','Arnelle','De la cruz',0,1,'2026-10-18 14:38:27.133205','gheanmamaw@gmail.com','',NULL,'2026-10-18 14:38:27.883496',0),(29,'pbkdf2_sha256$720000$8QILfaCyWahOhyHzNIqiYc$/Hb63/wJT7zG+zboFC1+GP0+wXInVDi3BRg1GapOAek=','2026-10-18 16:08:12.643190',0,'ghean','Ghean','De La Cruz',0,1,'2026-10-18 16:08:11.655437','gheanghean09@gmail.com','',NULL,'2026-10-18 16:08:12.626206',0);
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_conversation`
--

DROP TABLE IF EXISTS `chat_conversation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chat_conversation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `engine_preference` varchar(12) NOT NULL,
  `language` varchar(12) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `chat_conversation_user_id_15357b84_fk_auth_user_id` (`user_id`),
  CONSTRAINT `chat_conversation_user_id_15357b84_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_conversation`
--

LOCK TABLES `chat_conversation` WRITE;
/*!40000 ALTER TABLE `chat_conversation` DISABLE KEYS */;
INSERT INTO `chat_conversation` VALUES (45,'hello','2026-10-18 14:39:03.449958','2026-10-18 15:26:08.251742',28,'primary','en'),(49,'hi','2026-10-18 16:08:19.969205','2026-10-18 16:21:15.257322',29,'primary','en');
/*!40000 ALTER TABLE `chat_conversation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_message`
--

DROP TABLE IF EXISTS `chat_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `chat_message` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `role` varchar(10) NOT NULL,
  `content` longtext NOT NULL,
  `engine` varchar(64) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `conversation_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `chat_message_conversation_id_a1207bf4_fk_chat_conversation_id` (`conversation_id`),
  CONSTRAINT `chat_message_conversation_id_a1207bf4_fk_chat_conversation_id` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversation` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=375 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_message`
--

LOCK TABLES `chat_message` WRITE;
/*!40000 ALTER TABLE `chat_message` DISABLE KEYS */;
INSERT INTO `chat_message` VALUES (285,'user','hello','','2026-10-18 14:39:03.457230',45),(286,'assistant','Hi there! KNIGHT here — ask me anything about KCC enrollment, offices, teachers, or rooms.','KNIGHT','2026-10-18 14:39:04.373152',45),(287,'user','how many years kcc operating?','','2026-10-18 14:39:24.719189',45),(288,'assistant','I’m sorry, but I couldn’t find that information. For details on how long KCC has been operating, please check with the KCC administration office.','KNIGHT v1.0','2026-10-18 14:39:27.997461',45),(289,'user','what year kcc started?','','2026-10-18 14:39:39.352263',45),(290,'assistant','I’m sorry, but I couldn’t find that information. For details on when KCC started, please check with the KCC administration office.','KNIGHT v1.0','2026-10-18 14:39:41.592690',45),(291,'user','school hymm','','2026-10-18 14:39:49.655255',45),(292,'assistant','Here are the complete lyrics of the **KCC Alma Mater Hymn**:\n\n```\nAlma Mater Dear, all hail to you!\nAll hail to you.\nKabankalan Catholic College\nOur haven of pain, of joy and glory\nTo your teachings and ideals\nWe\'ll ever cling\nAmidst the toils and trials life may bring\nGuardian and light of our young lives\nStruggles and pains and frustrations\nAre to us the pillars to lean on.\nFor in your portals and inspirations\nWe\'ve built our hopes, our dreams and our ambitions,\nEven when we\'ll leave you dear school\nBeautiful memories will linger on.\n```\n\nComposer: Sr. Marie Josephine Antonio, SPC  \nLyrics: Miss Ester Besas\n\nFeel free to sing it with pride! ????','KNIGHT v1.0','2026-10-18 14:39:52.070955',45),(297,'user','what year kcc started?','','2026-10-18 14:41:00.322614',45),(298,'assistant','KCC was founded in **2027**.','KNIGHT v1.0','2026-10-18 14:41:06.477461',45),(299,'user','what is the bishop of kabankalan city?','','2026-10-18 14:42:26.280494',45),(300,'assistant','I’m sorry, but I couldn’t find that information. For details on the current Bishop of Kabankalan City, please check with the Diocese of Kabankalan office.','KNIGHT v1.0','2026-10-18 14:42:28.844248',45),(301,'user','the past bishop','','2026-10-18 14:42:40.504333',45),(302,'assistant','I couldn’t locate a definitive list of past bishops for Kabankalan City in the sources I searched. One result is a YouTube video titled “Ang atibg dating mahal na OBISPO Most Rev. TONY,” which appears to discuss a former bishop named Most Rev. Tony. For a complete and accurate list, you may want to contact the KCC office or the local diocese.','KNIGHT v1.0','2026-10-18 14:42:43.999646',45),(305,'user','what is the first name of kcc?','','2026-10-18 14:44:25.661450',45),(306,'assistant','The first name of KCC is **Kabankalan**.','KNIGHT v1.0','2026-10-18 14:44:31.610909',45),(307,'user','i mean the old name of kabankalan catholic college','','2026-10-18 14:44:42.743134',45),(308,'assistant','Ang dating pangalan ng Kabankalan Catholic College ay **Kabankalan Institute**.','KNIGHT v1.0','2026-10-18 14:44:45.896660',45),(311,'user','what is the past names of kcc?','','2026-10-18 14:45:47.545450',45),(312,'assistant','The only past name that’s documented for Kabankalan Catholic College is **Kabankalan Private Academy** (used in 1940). If you need more details, you might want to check the school archives or ask the administration office.','KNIGHT v1.0','2026-10-18 14:45:54.933704',45),(313,'user','what is the process of enrollment?','','2026-10-18 15:08:49.167649',45),(314,'assistant','Here’s the KCC enrollment process in a nutshell:\n\n1. **Submit Requirements** – Fill out the application form and bring the required documents.  \n2. **Entrance Examination** – Take the exam to show your academic readiness.  \n3. **Interview** – Meet the admissions committee for a brief interview.  \n4. **Enrollment** – Complete the paperwork and officially become a KCC student.\n\n**Documents you’ll need on enrollment day**  \n- Completed Application Form  \n- Report Card / Form 138  \n- Certificate of Good Moral Character  \n- PSA Birth Certificate  \n- 2 × 2 ID photos (4 pieces)  \n- Honorable Dismissal (for transferees)\n\nIf you’re ready to enroll for the 2025‑2026 school year, just visit the Registrar’s Office or contact the admissions team for details and to secure your slot. Good luck! ????','KNIGHT v1.0','2026-10-18 15:08:51.295850',45),(317,'user','process of enrollment','','2026-10-18 15:10:22.616666',45),(318,'assistant','Here’s the enrollment process in English:\n\n1. **Submit Requirements** – Fill out the application form and bring the required documents.  \n2. **Entrance Examination** – Take the exam to assess your academic readiness.  \n3. **Interview** – Attend a brief interview with the admissions committee.  \n4. **Enrollment** – Complete the enrollment paperwork and officially become a KCC student.\n\n**Documents you’ll need on enrollment day**  \n- Completed Application Form  \n- Report Card / Form 138  \n- Certificate of Good Moral Character  \n- PSA Birth Certificate  \n- 2 × 2 ID photos (4 pieces)  \n- Honorable Dismissal (for transferees)\n\nIf you’re ready to enroll for the 2025‑2026 school year, just visit the Registrar’s Office or contact the admissions team for details and to secure your slot. Good luck! ????','KNIGHT v1.0','2026-10-18 15:10:29.270935',45),(319,'user','how to enroll?','','2026-10-18 15:12:47.618964',45),(320,'assistant','To enroll at KCC, just follow these simple steps:\n\n1. **Fill out the Application Form** – You can get it from the Registrar’s Office or download it from the KCC website.  \n2. **Gather the Required Documents** –  \n   • Completed Application Form  \n   • Report Card / Form 138  \n   • Certificate of Good Moral Character  \n   • PSA Birth Certificate  \n   • 2 × 2 ID photos (4 pieces)  \n   • Honorable Dismissal (if you’re a transfer student)  \n3. **Submit Your Documents** – Bring everything to the Registrar’s Office.  \n4. **Take the Entrance Exam** – The exam will be scheduled by the admissions team.  \n5. **Attend the Interview** – Meet the admissions committee for a brief chat.  \n6. **Complete Enrollment** – Sign the enrollment forms and pay any required fees.  \n\nAfter that, you’re officially a KCC student! If you need help or have questions, just drop by the Registrar’s Office or call the admissions office. Good luck! ????✨','KNIGHT v1.0','2026-10-18 15:12:50.055074',45),(321,'user','how to take car pass?','','2026-10-18 15:13:14.369788',45),(322,'assistant','To get a car pass, just head over to the **HR Office**. They’ll handle the application and give you the pass. If you need any forms or further details, ask the HR staff there. ????✨','KNIGHT v1.0','2026-10-18 15:13:16.571399',45),(323,'user','how to go cr?','','2026-10-18 15:14:09.022518',45),(324,'assistant','From the main gate, walk straight down the hallway. Keep going until you pass the CR (the CR area) and the exit gate. That’s the route to reach the CR. ????????','KNIGHT v1.0','2026-10-18 15:14:11.249431',45),(325,'user','kcc is under ched?','','2026-10-18 15:14:42.790728',45),(326,'assistant','I’m sorry, but I couldn’t find that information. For clarification, you might want to check with the KCC administration office.','KNIGHT v1.0','2026-10-18 15:14:45.393526',45),(327,'user','what is the activity in kcc?','','2026-10-18 15:17:32.238919',45),(328,'assistant','I’m sorry, but I couldn’t find that information. For details on activities, you might want to check with the KCC administration office.','KNIGHT v1.0','2026-10-18 15:17:34.099437',45),(335,'user','what date of kcc week?','','2026-10-18 15:20:28.961151',45),(336,'assistant','KCC Week (or KCC Days) is celebrated during the first week of December. ????','KNIGHT v1.0','2026-10-18 15:20:34.756512',45),(337,'user','ok','','2026-10-18 15:21:32.962828',45),(338,'assistant','Glad to help! If you have any more KCC questions, just let me know.','KNIGHT v1.0','2026-10-18 15:21:35.055626',45),(341,'user','hi','','2026-10-18 15:22:37.583216',45),(342,'assistant','Hello! I\'m KNIGHT, your KCC campus assistant. What can I help you with today?','KNIGHT','2026-10-18 15:22:38.216986',45),(343,'user','hello','','2026-10-18 15:22:45.226807',45),(344,'assistant','Hi there! KNIGHT here — ask me anything about KCC enrollment, offices, teachers, or rooms.','KNIGHT','2026-10-18 15:22:45.959109',45),(349,'user','what is the owner of kcc lights and sound?','','2026-10-18 15:25:40.606387',45),(350,'assistant','I’m sorry, but I couldn’t find information on the owner of KCC Lights and Sound in the knowledge base. For that detail, you might want to check with the KCC administration office or the Lights and Sounds team directly.','KNIGHT v1.0','2026-10-18 15:25:47.110761',45),(351,'user','owner of kcc lights and sound?','','2026-10-18 15:25:57.264070',45),(352,'assistant','I’m sorry, but I couldn’t find information on the owner of KCC Lights and Sound. You might want to ask the KCC administration office or the Lights and Sounds team for that detail.','KNIGHT v1.0','2026-10-18 15:25:59.371898',45),(353,'user','the manager','','2026-10-18 15:26:06.002227',45),(354,'assistant','I’m sorry, but I couldn’t find information on the manager of KCC Lights and Sound. You may want to check with the KCC administration office or the Lights and Sounds team for that detail.','KNIGHT v1.0','2026-10-18 15:26:08.247576',45),(355,'user','hi','','2026-10-18 16:08:19.976513',49),(356,'assistant','Hello! I\'m KNIGHT, your KCC campus assistant. What can I help you with today?','KNIGHT','2026-10-18 16:08:20.628399',49),(357,'user','schedule of exam','','2026-10-18 16:08:39.854080',49),(358,'assistant','Sure! For the 2026‑2027 school year, the mid‑term exams for college courses are scheduled on **17, 19, and 20** of the month (the exact month isn’t specified in the info we have). If you need more details—like specific dates, times, or which classes are on each day—please let me know or check the official KCC exam calendar posted on campus.','KNIGHT v1.0','2026-10-18 16:08:42.517125',49),(359,'user','kcc hymm','','2026-10-18 16:08:56.013970',49),(360,'assistant','Here are the complete lyrics of the **KCC Alma Mater Hymn**:\n\n**Composer:** Sr. Marie Josephine Antonio, SPC  \n**Lyrics:** Miss Ester Besas  \n\n```\nAlma Mater Dear, all hail to you!\nAll hail to you.\nKabankalan Catholic College\nOur haven of pain, of joy and glory\nTo your teachings and ideals\nWe\'ll ever cling\nAmidst the toils and trials life may bring\nGuardian and light of our young lives\nStruggles and pains and frustrations\nAre to us the pillars to lean on.\nFor in your portals and inspirations\nWe\'ve built our hopes, our dreams and our ambitions,\nEven when we\'ll leave you dear school\nBeautiful memories will linger on.\n```\n\nFeel free to sing it with pride! ????','KNIGHT v1.0','2026-10-18 16:08:58.624090',49),(361,'user','kcc mission and vision','','2026-10-18 16:09:08.347658',49),(362,'assistant','**Kabankalan Catholic College (KCC)**  \n\n**Vision**  \n“Kabankalan Catholic College, Inc., as builder of the future, is a Christ‑centered learning community of accountable and socially responsible individuals, that leads positive change, responds to and serves the mission of the Diocese, the nation, and the world.”  \n\n**Mission**  \n“KCC commits to provide quality and inclusive Catholic education, rooted in the Gospel and driven by innovative research and meaningful community engagements, empowering its members to become effective agents of societal transformation.”','KNIGHT v1.0','2026-10-18 16:09:10.501418',49),(363,'user','who is the current president','','2026-10-18 16:09:26.421365',49),(364,'assistant','The current president of Kabankalan Catholic College is **Rev. Fr. Richard Lachica**.','KNIGHT v1.0','2026-10-18 16:09:29.797397',49),(365,'user','what is the 7.1 in the student handbook','','2026-10-18 16:18:47.562265',49),(366,'assistant','**Section 7.1 – SUMMARY PROCEEDINGS**  \nThis part of the student handbook explains how disciplinary action is handled. It states that, after due‑process requirements are met, the procedure is summarized in nature. The student is assisted by a parent/guardian or counsel, parents are properly informed, and they are called to attend a conference in the Office of the Principal. First‑ and second‑offense students receive a reprimand or warning, while habitual violators may face higher administrative penalties. Restitution and retribution may also be required.','KNIGHT v1.0','2026-10-18 16:18:54.701136',49),(367,'user','vandalizing','','2026-10-18 16:19:47.494481',49),(368,'assistant','I’m sorry, but I couldn’t find any specific information about “vandalizing” in the KCC student handbook. For details on that policy, please check the handbook directly or contact the Office of the Principal.','KNIGHT v1.0','2026-10-18 16:19:49.936932',49),(369,'user','haircut policy','','2026-10-18 16:20:04.857973',49),(370,'assistant','I’m sorry, but I couldn’t find any information about a hair‑cutting policy in the KCC student handbook. For that detail, please check the handbook directly or ask the Office of the Principal.','KNIGHT v1.0','2026-10-18 16:20:07.399052',49),(371,'user','HAIR CUT POLICY','','2026-10-18 16:20:44.825978',49),(372,'assistant','I’m sorry, but I couldn’t find any information about a haircut policy in the KCC student handbook. For that detail, please check the handbook directly or ask the Office of the Principal.','KNIGHT v1.0','2026-10-18 16:20:52.097474',49),(373,'user','1.1 of stuent hand book','','2026-10-18 16:21:13.132656',49),(374,'assistant','I’m sorry, but I couldn’t locate section 1.1 of the KCC Student Handbook in the information I have. Please refer to the handbook itself or contact the Office of the Principal for that specific section.','KNIGHT v1.0','2026-10-18 16:21:15.253415',49);
/*!40000 ALTER TABLE `chat_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (7,'accounts','user'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(8,'chat','conversation'),(11,'chat','knowledgecategory'),(12,'chat','knowledgeitem'),(9,'chat','message'),(4,'contenttypes','contenttype'),(6,'info','info'),(5,'sessions','session'),(10,'users','user');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (22,'contenttypes','0001_initial','2026-10-13 03:09:53.677832'),(23,'contenttypes','0002_remove_content_type_name','2026-10-13 03:09:53.684440'),(24,'auth','0001_initial','2026-10-13 03:09:53.688662'),(25,'auth','0002_alter_permission_name_max_length','2026-10-13 03:09:53.698686'),(26,'auth','0003_alter_user_email_max_length','2026-10-13 03:09:53.706152'),(27,'auth','0004_alter_user_username_opts','2026-10-13 03:09:53.712711'),(28,'auth','0005_alter_user_last_login_null','2026-10-13 03:09:53.717347'),(29,'auth','0006_require_contenttypes_0002','2026-10-13 03:09:53.721631'),(30,'auth','0007_alter_validators_add_error_messages','2026-10-13 03:09:53.725160'),(31,'auth','0008_alter_user_username_max_length','2026-10-13 03:09:53.729043'),(32,'auth','0009_alter_user_last_name_max_length','2026-10-13 03:09:53.735313'),(33,'auth','0010_alter_group_name_max_length','2026-10-13 03:09:53.739234'),(34,'auth','0011_update_proxy_permissions','2026-10-13 03:09:53.742859'),(35,'auth','0012_alter_user_first_name_max_length','2026-10-13 03:09:53.746952'),(36,'users','0001_initial','2026-10-13 03:09:53.751129'),(37,'admin','0001_initial','2026-10-13 03:09:53.755151'),(38,'admin','0002_logentry_remove_auto_add','2026-10-13 03:09:53.758832'),(39,'admin','0003_logentry_add_action_flag_choices','2026-10-13 03:09:53.762963'),(40,'sessions','0001_initial','2026-10-13 03:09:53.768588'),(41,'chat','0001_initial','2026-10-16 13:46:02.450217'),(42,'chat','0002_conversation_engine_preference_conversation_language','2026-10-16 13:58:57.593305'),(43,'chat','0003_remove_knowledgeitem_category_and_more','2026-10-16 14:28:15.294019'),(44,'chat','0004_alter_conversation_engine_preference','2026-10-17 11:29:12.971908'),(45,'users','0002_user_is_permanently_deactivated','2026-10-17 12:27:23.617334');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0bed1fsu2xnxvu6eeykxkc3gyxxd1wmg','.eJxVjDEOwjAMAP_iGUW0jRPckb1vqBzbkAJqpKadEH9HlTrAene6N4y8rXncqi3jpNADwemXJZanzbvQB8_34qTM6zIltyfusNUNRe11Pdq_QeaaoQdsyFgTtqIskSigaGdIrCkYmgVhEi92iV2MaP6GTYtnjGbUeu4ifL4TwjiH:1xHift:pLdi1U2FTCp6W8iEh0SdodvCl0ND8uot3-p7BbODH18','2026-10-30 14:12:45.214168'),('0sau5216q3tx17rot8o3livquz4z2s1v','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSJy:0XasWos6Cd8gnLJr3An5VwC84P18wXsDKGdXsU1BW5w','2026-10-27 02:32:54.345272'),('19ds16m57qf1xdgqidpeeqbg13foqsae','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSwD:bCCTZuv0cboqQBcMNiY_wKO8GtScfeyB-4HIyelMJQw','2026-10-27 03:12:25.222173'),('2ejvwxncz1p24oia1v28blutchxb0x62','.eJxVjEEOwiAQAP-yZ0OAslB69O4bml1YpGrapLQn499Nkx70OjOZN4y0b3Xcm6zjlGEA6-DyC5nSU-bD5AfN90WlZd7WidWRqNM2dVuyvK5n-zeo1CoM0JWe0Uoy6G0Q0lKceE1kkG3QLkZMTBgSY1eyNiERWuN9X3KJ7HWEzxcQUDgy:1xI2dR:-25gAL3bW0VImUkOBu4zDWzVOxZmyC93KUFhM-uI6xM','2026-10-31 11:31:33.084349'),('2g5awh4kw0jzy59f5opueylqngmeik75','.eJxVjDEOgzAMAP_iuYogMZAyducNkWM7DW0VJAJT1b9XSAztene6NwTatxz2qmuYBUZoHVx-YSR-ajmMPKjcF8NL2dY5miMxp61mWkRft7P9G2SqGUZw1HvUVtihR-RuiKxJxSImdI1gw73vCFPylqNcVQUJxZLH5CwPFj5fGzo4xQ:1xHixa:136Q86VDAXu9l_ge9vvhA0r8iC1KkL5Fq0f00UVRRcs','2026-10-30 14:31:02.752450'),('2jf5k1scum2ce70d3aszoei502u3i9xj','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSvd:iAo1fcFE4TnISJ_CrsMOOR6tLUVzJyR5_Rs5OFx4JuU','2026-10-27 03:11:49.530796'),('3c1l17t9nublwhofh5yd8o5sgbsljb1g','.eJxVjDkOwjAQAP-yNbLWTtZHSnreYK2P4ACypTipEH9HkVJAOzOaN3jet-L3nle_JJhAwuWXBY7PXA-RHlzvTcRWt3UJ4kjEabu4tZRf17P9GxTuBSaIMrtBoZ61StalYFw0xGgiEWZJLNGNirTUg80xWbQzMjoaKKBWaiT4fAHC0DZ-:1xGR07:4d_QpsBXHjH8fo_K6rhNljQYrW2v28S0Jj7JO2PhvYo','2026-10-27 01:08:19.260663'),('aatmygax7kml61ve3n6i8fg17kdtzy24','.eJxVjMsOgjAQAP9lz6ZZtm-O3v2GZtsughpIKJyM_25IOOh1ZjJvSLxvY9qbrGmq0EOHcPmFmctT5sPUB8_3RZVl3tYpqyNRp23qtlR5Xc_2bzByG6GHoQxUfQ2WnC_EBl0wjFpQMKKYnAvb4LXXxlpDuvgoURNV6lxAlAifL_opNxA:1xHivt:eoh572Q98aqyZb0gV7Sz9kLL3j4RYl-WeAlA2D32JPI','2026-10-30 14:29:17.606495'),('aqhriv4uhotad1p5qav3ign08p1cpvmw','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSKD:UwZzR-PRZ4XolJ9mCWjrGcRWqRniKHTgWg5Gtq7lmkU','2026-10-27 02:33:09.127474'),('bi2qy7wplkieqej8srvzeux1o1dlg35t','.eJxVjMsKwjAQAP9lzxLI5rX26N1vCLt5mKq00LSn4r9LoQe9zgyzQ-RtbXHrZYljhgEILr9MOL3KdIj85OkxqzRP6zKKOhJ12q7ucy7v29n-DRr3BgNIrmLQWeu9sakShhK086FWL-aaCJGIRddQAmstCYnIluAwcUXjHXy-34k3jw:1xHiYB:UT_t_WSGsbJCuH3KBNInKFK9dTdsbnhs6HESvWOvvtg','2026-10-30 14:04:47.325831'),('bqbns39bdlmga6x9uqdspud7mjf5qhvk','.eJxVjDkOwjAQAP-yNbJ8rO04JT1vsNbH4gBKpDipEH9HkVJAOzOaN0Tatxb3Xtc4FRhBIVx-YaL8rPNhyoPm-yLyMm_rlMSRiNN2cVtKfV3P9m_QqDcYwaHjMBgmZGJjFCetrURGhWHQqRAbT1X6ZHyoPviKWjpLNqdsuRDC5wsEljg-:1xHkcQ:zsca-Qh1ufXt5g80lbKZsenEbov_VpUk7PmO46eYD1k','2026-10-30 16:17:18.858245'),('ck32tqc6htidvcpnvf7nzchzyji519us','.eJxVjEsKwjAUAO_y1hKSpslrunTvGcL7BFOVFpp2Jd5dCl3odmaYN2Tat5r3VtY8KYzQdXD5hUzyLPNh9EHzfTGyzNs6sTkSc9pmbouW1_Vs_waVWoURCNU7Yi4pBFFE1SDOCzk7JExR2Q6csPjYE1Hw1opD7LsoUZmRAny-HdA4Ww:1xI2ZO:T5tru9oFJLTFLDPAFOk6ml_ZC4HJw3-MVhRzjnjIu8Y','2026-10-31 11:27:22.780981'),('ddeeiehf4ysx2qedp3d1mbtvblvp8cqy','.eJxVjLsOgkAQAP9la3O5BeH2KO39BrIvBTWQcFAZ_92QUGg7M5k39LytQ78VX_rRoAMkOP1CYX36tBt78HSfg87TuowS9iQctoTrbP66HO3fYOAyQAeCFluqqMaUUbxOhuRnslxpLYxRNVOFtzY7JW1YTRImZ3HKsYm5gc8X-4U35g:1xI1sb:sjsis8nlFLnBdgU6b3WAunu9cQAK4PsXBHv4Jti0uKs','2026-10-31 10:43:09.761215'),('e6vxs3ao49qvqwn93sdqzxfndhdic7q4','.eJxVjDkOwjAQAP-yNbLWTtZHSnreYK2P4ACypTipEH9HkVJAOzOaN3jet-L3nle_JJhAwuWXBY7PXA-RHlzvTcRWt3UJ4kjEabu4tZRf17P9GxTuBSaIMrtBoZ61StalYFw0xGgiEWZJLNGNirTUg80xWbQzMjoaKKBWaiT4fAHC0DZ-:1xGR3f:K9KfN5fG4k0pRF4CclU893MOkL66S_BOt6pXFGiPpH8','2026-10-27 01:11:59.149094'),('erfc1zde61dqzmhyxe4m2qii2hj1d710','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSCV:wIbYdLXyAifRbKa2ngvGmS6omXrfw3DtnwYtpRqUmmQ','2026-10-27 02:25:11.666229'),('ffcy97mpy1urx3vunt95jya61wfj3iav','.eJxVjM0OwiAQBt9lz4YALaX06N1naD52QaqGJv05Gd_dNOlBrzOTedOIfSvjvqZlnIQGMh1dfmEEP1M9jDxQ77PiuW7LFNWRqNOu6jZLel3P9m9QsBYaqEf2NlqTjO5Tdpp9nxFDm4MzaLTvHAJz4yOzBOPabDubRADtETJAny8Xozjy:1xI1nq:7ngG23qficuE6t9TMY6_78qnUoWTgEqV1I9AIXjoNWQ','2026-10-31 10:38:14.903008'),('h15fq7ls8b6fkqeynoyur8lvps7hws3m','.eJxVjDEKwzAMAP-iuRgUK7GdsXvfYGRLbtIWB-JkKv17CWRo17vj3hB536a4N13jLDACOrj8wsT5qfUw8uB6X0xe6rbOyRyJOW0zt0X0dT3bv8HEbYIReEgceuqKDFQ0hY5zLxSsH5AdqydLvRbJ6MQ7X1yhhF1gS-QwI1r4fAEfFDgW:1xI1oA:-aOjsAhjlve13bSk8uqNAcWFfJ01VZvFVaOpShsDbo8','2026-10-31 10:38:34.686303'),('h6wdat46ay702udjn9hrle4hz7wjiayn','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSKT:iucQq76WKUIaV03iHhbhtblD83eFeNnNLdqY4uyDKbQ','2026-10-27 02:33:25.344857'),('igjnwibrn4b6re93mxaif3c72k0vsmhi','.eJxVjLsOgzAMAP_FcxXhOEDM2L3fgOw4KbQVSDymqv9eITG0693p3tDLvg39vualHw068AiXX6iSnnk6jD1kus8uzdO2jOqOxJ12dbfZ8ut6tn-DQdYBOuCEgamEyMVi05j3VSyhwqZW8lizUluHxJVEDogqZqwkRuqR2kgCny_cWDcW:1xI25s:rGO0WFEZCvRJsEVHmFQFW4c0Eyl2Nvo6-tCJmQHcImw','2026-10-31 10:56:52.844934'),('ip3hau8fm9z1k11ircdhwmjmucinoxrb','.eJxVjDkOwjAQAP-yNbLsjc-U9LzB8rHGAWRLcVIh_o4ipYB2ZjRv8GHfqt8HrX7JMIOByy-LIT2pHSI_Qrt3lnrb1iWyI2GnHezWM72uZ_s3qGFUmCFwi6pIzVOMxmkUZLNAE6zLBp2MmstJKU1oi0SVUpECBcnopuTUlAk-X8VnNyE:1xHiSm:7lh4W1GaEX4vz368kFdzCCR5hFSVKEA58TrPS_zBPj0','2026-10-30 13:59:12.537068'),('jlnvfvnva5atphi5nunl04ytb1udyald','.eJxVjDsOwyAQBe-ydYQwC-vgMr3PgJaPg5MIJGNXUe4eIblIyjczem9wfOzZHS1tbo0wwWDh8gs9h2cq3cQHl3sVoZZ9W73oiThtE3ON6XU727-DzC3DBIm0QSsD66tFbxUuyGOg0SolByRjFkmsEb0mTTYkpjh4bfpgJTHA5wvZwja7:1xI1sr:gQnjUQ95XjkzkdAVFI0_Hi60F-HUq8yOqqKFJO6dEyM','2026-10-31 10:43:25.658396'),('k35utexpxp34zur0kd7n1c1m9io4gix8','.eJxVjLsOwjAMAP_FM4rSpkncjux8Q2QnNimgVupjQvw7qtQB1rvTvSHRvtW0r7KkscAAAS6_jCk_ZTpEedB0n02ep20Z2RyJOe1qbnOR1_Vs_waV1goDMAbnFaPvgnPK2Ktlx45yUeptT5pb9KFpFLtWSucsKyPaGEUkaEb4fAHoLzhR:1xHiIS:s14mvR7en185kNyLLb2GNWC7_vh1yRF-E2LvWM2sn0M','2026-10-30 13:48:32.341123'),('kxc7ftbkj0em8f67dzs34xvvlh9ucoxe','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSLi:_kgstk1Ttz6r5hyMKO45BY6170jVIKnzaAUCCjA2bHo','2026-10-27 02:34:42.157496'),('m3doaqi0tde61sydxmd6y0u1ypzq53ks','.eJxVjDkOwjAQAP-yNbLs9RE7JT1viLzeNQ6gRMpRIf6OIqWAdmY0bxjyvrVhX2UZRoYeHFx-GeXylOkQ_MjTfVZlnrZlJHUk6rSrus0sr-vZ_g1aXhv0kHJCtDEgBud1ClRsCpy4CkdxGDkQ6eo76XRlHdAXQeMNWSPRFirw-QLKJzeu:1xHiHb:WaF4KV6mwRGUE4RtPA9IfucObqvNTIdt6Q0O7FiThrA','2026-10-30 13:47:39.819832'),('noa5runjj7padq7uk3x8rcobuko94urt','.eJxVjDEOgzAMAP_iuYpCnABm7N43IMc2hbYCicBU9e8VEkO73p3uDT3v29jvxdZ-UuggIFx-YWZ52nwYffB8X5ws87ZO2R2JO21xt0XtdT3bv8HIZYQOhKKgxgE1E1WEtbQcB84-cFJDTx6lTlg1SZJYSpilDdJoRRQjW4DPFw9fOAc:1xI2bE:ytVENXGqYh_XKtuGI7nDZ2Ep-ORag01DpEW4yfjV2sg','2026-10-31 11:29:16.779235'),('oo7qpndoa5yck2rh9uaocai1945v9tre','.eJxVjLsOwjAMAP_FM4qS1CFpR_Z-Q2U7DimgVupjQvw7qtQB1rvTvWGgfavDvuoyjBk68Akuv5BJnjodJj9ous9G5mlbRjZHYk67mn7O-rqd7d-g0lqhgxRKJvIuYW6804ihDY5TQm6DF7Uhii-OY2ZUtNxg21hkIXFF41UKfL7-2zg0:1xIS2E:TX6OQLNIu-gSZpRpFSsFFZWaNjLwdf0Pwfs_6cFdMlM','2026-11-01 14:38:50.865360'),('p87mhkblsonnyb8cvcbj5iuc0lce0ur7','.eJxVjEEKwyAQAP-y5yJxFWNy7L1vkHVda9piICan0r8XIYf2OjPMGwIdewlHky0sCWbQCJdfGImfUrtJD6r3VfFa922JqifqtE3d1iSv69n-DQq1AjMgepssIekxm6zRSDbeZxycYBQ2dtKOjXYcMw8xshVHvlMrY5rQwecLANg3_A:1xHixY:qM134811C8pW_QTygwOVsPpUIrDYtb8pjT31Tbienmo','2026-10-30 14:31:00.578964'),('px20davmc86r08dsknhsbcrxbo8d2phr','.eJxVjDEOwjAMRe_iGUWOG0joyN4zVHYS0wJKpaadEHdHkTrA-N97-m8Yed-mca95HecEPRDC6RcKx2cuzaQHl_ti4lK2dRbTEnPYaoYl5dftaP8OJq4T9MDCGIi8qD0j-kiujaCMlh0SInsblKIT1wVGScqBVFE7b_XSXeHzBfKaN6U:1xI1xr:hdZncJJ45DhkveIMIKg_DZ-Kyyk7DsTG3BjH-Dwio3k','2026-10-31 10:48:35.254478'),('rldzw6s3kdiwybnnng669tkabevq1k7t','.eJxVjM0KwjAQBt9lzxJok2yTHr37DGU3-WqqkkJ_TuK7S6EHvc4M86ZB9q0M-4plmDL15Onyy1TSE_UQ-SH1Pps0122Z1ByJOe1qbnPG63q2f4Mia6GeWLQNcQwWjYfzkE7ZwUYgA46R4Dz7hpFiaDPYQ0OnFo200bKO9PkCAdg4uA:1xHiI8:XLQTeJLRVOhqYlVAfIiQES-HL_DsN0fk-LMp8X3ZNAU','2026-10-30 13:48:12.264094'),('s2rykmmc05ift4n4wx851dksii803k18','.eJxVjMsOwiAQAP9lz4YsdKHYo_d-QwPLIlUDSR8n47-bJj3odWYyb5jCvpVpX2WZ5gQDdHD5ZTHwU-oh0iPUe1Pc6rbMUR2JOu2qxpbkdTvbv0EJa4EBRCwb7Cm6jBx0ZEYyWTuN1yQadSJEyy77rpNeiBIRebJRe8zovYHPF-IsNyg:1xHiHK:Q3b-j2VrnN_22SFh5TqJc04i0Mmljw5m146VG0ujjqE','2026-10-30 13:47:22.593942'),('sqqxsl591s3naw19fzq39y05ra8hv0md','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSRZ:rgzSrX03tnQbIMLDIFtqR696SzypRzyAuCfd8zO_r4s','2026-10-27 02:40:45.631887'),('tpbqj4bfslh3gw5rm8qei7ao5op32grq','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSzN:MwNSWIX-SUTuXeIzXO5vZhLSLhA3vyiyEAFRKhygnzc','2026-10-27 03:15:41.344742'),('w0vu9dfdbs94r75112t7x0rg6jcqhmz1','.eJxVjLsOwjAMAP_FM4qS1CFpR_Z-Q2U7DimgVupjQvw7qtQB1rvTvWGgfavDvuoyjBk68Akuv5BJnjodJj9ous9G5mlbRjZHYk67mn7O-rqd7d-g0lqhgxRKJvIuYW6804ihDY5TQm6DF7Uhii-OY2ZUtNxg21hkIXFF41UKfL7-2zg0:1xIS5E:2wg_qyh_2Dss_bJHEW7aTTcrXVP30dgHIU4eRO-1nWo','2026-11-01 14:41:56.143232'),('w610qr9361r36lj00ss0jsozanweiqte','.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSur:fS1PMj53Lt44G6JQpoZcQ4CZqIZvqTc65Ap3mdADsoQ','2026-10-27 03:11:01.792708'),('xo35m4vj4k6mowstcbq9zl8dyny6e0dd','.eJxVjDEOwjAMRe-SGUUtdpyUkZ0zVI7j0AJKpKadEHdHlTrA-t97_21G3tZp3Jou45zMxfTOnH7HyPLUspP04HKvVmpZlznaXbEHbfZWk76uh_t3MHGb9jq4rMpM2GcFiUpd5xwiBeLB9wk69ojgQMkPXgKAUNYYkATxnMF8vg3GN7k:1xI1nb:wwGzEVSFlZrl4acuad3i_VK9n07cv2t8DadrKamtkPY','2026-10-31 10:37:59.255586'),('zdp74xhjexq6hm3xxd3d5nf22ob6dg11','.eJxVjEEOwiAQAP-yZ0Ngha706N03EGAXqRqalPZk_Ltp0oNeZybzhhC3tYatyxImhhHQwekXppif0nbDj9jus8pzW5cpqT1Rh-3qNrO8rkf7N6ixVxjB-JS1M6QleUvkzTA4tlqKRkOGkHI6Zy2MUhgzki_WCdsoZC7ssMDnC-14N9k:1xI2g7:N1i0H5gJSEnkCzI4cbjQcKU0SW06wYgQAa5wECy6fg0','2026-10-31 11:34:19.136867');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-19  7:11:51
