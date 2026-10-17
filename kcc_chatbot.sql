-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 17, 2026 at 06:00 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `kcc_chatbot`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add info', 6, 'add_info'),
(22, 'Can change info', 6, 'change_info'),
(23, 'Can delete info', 6, 'delete_info'),
(24, 'Can view info', 6, 'view_info'),
(25, 'Can add user', 7, 'add_user'),
(26, 'Can change user', 7, 'change_user'),
(27, 'Can delete user', 7, 'delete_user'),
(28, 'Can view user', 7, 'view_user'),
(29, 'Can add conversation', 8, 'add_conversation'),
(30, 'Can change conversation', 8, 'change_conversation'),
(31, 'Can delete conversation', 8, 'delete_conversation'),
(32, 'Can view conversation', 8, 'view_conversation'),
(33, 'Can add message', 9, 'add_message'),
(34, 'Can change message', 9, 'change_message'),
(35, 'Can delete message', 9, 'delete_message'),
(36, 'Can view message', 9, 'view_message'),
(37, 'Can add user', 10, 'add_user'),
(38, 'Can change user', 10, 'change_user'),
(39, 'Can delete user', 10, 'delete_user'),
(40, 'Can view user', 10, 'view_user'),
(41, 'Can add knowledge category', 11, 'add_knowledgecategory'),
(42, 'Can change knowledge category', 11, 'change_knowledgecategory'),
(43, 'Can delete knowledge category', 11, 'delete_knowledgecategory'),
(44, 'Can view knowledge category', 11, 'view_knowledgecategory'),
(45, 'Can add knowledge item', 12, 'add_knowledgeitem'),
(46, 'Can change knowledge item', 12, 'change_knowledgeitem'),
(47, 'Can delete knowledge item', 12, 'delete_knowledgeitem'),
(48, 'Can view knowledge item', 12, 'view_knowledgeitem');

-- --------------------------------------------------------

--
-- Table structure for table `auth_user`
--

CREATE TABLE `auth_user` (
  `id` bigint(20) NOT NULL,
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
  `is_permanently_deactivated` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_user`
--

INSERT INTO `auth_user` (`id`, `password`, `last_login`, `is_superuser`, `username`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`, `email`, `middle_name`, `birthday`, `created_at`, `is_permanently_deactivated`) VALUES
(1, 'pbkdf2_sha256$720000$enKzRw9eEKTzuFUKBU31Vx$TfrMBDANY1pDf1GXm8Fsq/a+yJs1rs7tEohiSPV4Z1w=', '2026-10-17 15:14:49.099133', 1, 'admin', '', '', 1, 1, '2026-10-08 16:25:02.510574', 'admin@admin.com', '', '2005-03-22', '2026-10-08 16:25:03.205923', 0),
(27, 'pbkdf2_sha256$720000$BUgmA9iOfe4q5HKXWEFxl8$i4Ru5hHWXPjP2LV48wfqsA2hYTehdgcITdZqmdTL2hI=', '2026-10-17 15:49:17.086615', 0, 'Gheanzkie', 'ghean', 'De La Cruz', 0, 1, '2026-10-17 14:58:46.286098', 'gheanghean09@gmail.com', '', NULL, '2026-10-17 14:58:47.118339', 0);

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_groups`
--

CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_user_user_permissions`
--

CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_conversation`
--

CREATE TABLE `chat_conversation` (
  `id` bigint(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `engine_preference` varchar(12) NOT NULL,
  `language` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_conversation`
--

INSERT INTO `chat_conversation` (`id`, `title`, `created_at`, `updated_at`, `user_id`, `engine_preference`, `language`) VALUES
(40, 'hello', '2026-10-17 14:58:52.022256', '2026-10-17 15:14:32.953616', 27, 'primary', 'en'),
(42, 'remember: the gym is closed monday to friday and open saturday and sunday', '2026-10-17 15:31:03.091916', '2026-10-17 15:48:31.827596', 1, 'primary', 'en'),
(43, 'remember: the coc building is located at the elementary', '2026-10-17 15:49:29.907540', '2026-10-17 15:59:46.057489', 27, 'primary', 'en');

-- --------------------------------------------------------

--
-- Table structure for table `chat_message`
--

CREATE TABLE `chat_message` (
  `id` bigint(20) NOT NULL,
  `role` varchar(10) NOT NULL,
  `content` longtext NOT NULL,
  `engine` varchar(64) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `conversation_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chat_message`
--

INSERT INTO `chat_message` (`id`, `role`, `content`, `engine`, `created_at`, `conversation_id`) VALUES
(235, 'user', 'hello', '', '2026-10-17 14:58:52.033852', 40),
(236, 'assistant', 'Hi there! KNIGHT here — ask me anything about KCC enrollment, offices, teachers, or rooms.', 'KNIGHT', '2026-10-17 14:58:52.616700', 40),
(247, 'user', 'reminder: ang location ng kcc ay nasa brgy 2', '', '2026-10-17 15:13:58.598031', 40),
(248, 'assistant', 'I’m sorry, but I couldn’t find any information indicating that KCC is located in Brgy. 2. According to the official details, KCC is at Guanzon St., Brgy. 1, Kabankalan City. If you need the most accurate address, it’s best to check the KCC website or contact them directly at (032) 4712‑479.', 'KNIGHT v1.0', '2026-10-17 15:14:00.841286', 40),
(249, 'user', 'tandaan: ang official location ng kcc ay nasa brgy 2', '', '2026-10-17 15:14:30.694413', 40),
(250, 'assistant', 'I’m sorry, but I couldn’t find any information indicating that KCC is located in Brgy. 2. According to the official details, KCC is at Guanzon St., Brgy. 1, Kabankalan City. If you need the most accurate address, it’s best to check the KCC website or contact them directly at (032) 4712‑479.', 'KNIGHT v1.0', '2026-10-17 15:14:32.949609', 40),
(261, 'user', 'remember: the gym is closed monday to friday and open saturday and sunday', '', '2026-10-17 15:31:03.104548', 42),
(262, 'assistant', 'Added to my knowledge base: \"the gym is closed monday to friday and open saturday and sunday\". Ask me about it anytime!', 'KNIGHT KB', '2026-10-17 15:31:03.111522', 42),
(263, 'user', 'the gym is open?', '', '2026-10-17 15:31:12.533703', 42),
(264, 'assistant', 'Yes! The gym is open on Saturdays and Sundays. If you’re planning to use it during the week, it’s closed from Monday to Friday. Enjoy your workout! ????️‍♂️\n\n(Noted: Gym Availability.)', 'KNIGHT v1.0', '2026-10-17 15:31:19.130377', 42),
(265, 'user', 'wheres located the cmat office?', '', '2026-10-17 15:46:47.440354', 42),
(266, 'assistant', 'The CMAT dean’s office is on the 2nd floor of the old building. From the main gate, take the first staircase up to the 2nd floor; the office is directly on that level.', 'KNIGHT v1.0', '2026-10-17 15:46:50.105454', 42),
(267, 'user', 'wheres located the ceas office?', '', '2026-10-17 15:47:08.796972', 42),
(268, 'assistant', 'I’m sorry, but I couldn’t find information on the CEAS office location. It might be best to check the campus directory or ask at the main information desk for the exact address.', 'KNIGHT v1.0', '2026-10-17 15:47:11.738699', 42),
(269, 'user', 'remember: the ceas building is located the back of highchool building, if you at the gate, straight the hallway until you passed the cr and the exit gate, keep straight and turn right and you will see the ceas building', '', '2026-10-17 15:48:15.182018', 42),
(270, 'assistant', 'Added to my knowledge base: \"the ceas building is located the back of highchool building, if you at the gate, straight the hallway until you passed the cr and the exit gate, keep straight and turn right and you will see the ceas building\". Ask me about it anytime!', 'KNIGHT KB', '2026-10-17 15:48:15.190499', 42),
(271, 'user', 'location of ceas office building', '', '2026-10-17 15:48:25.515888', 42),
(272, 'assistant', 'The CEAS building is at the back of the high‑school building. From the main gate, walk straight down the hallway until you pass the CR and the exit gate, keep going straight, then turn right—you’ll see the CEAS building.\n\n(Noted: Location of CEAS Office Building.)', 'KNIGHT v1.0', '2026-10-17 15:48:31.821055', 42),
(273, 'user', 'remember: the coc building is located at the elementary', '', '2026-10-17 15:49:29.923359', 43),
(274, 'assistant', 'I’m sorry, but I couldn’t find that information in the KCC knowledge base. For details about the COC building, please check with the campus office or the student services desk.', 'KNIGHT v1.0', '2026-10-17 15:49:32.644060', 43),
(275, 'user', 'anong araw bukas ang gym?', '', '2026-10-17 15:59:16.868533', 43),
(276, 'assistant', 'The KCC gym is open **Monday to Friday** and closed on **Saturday and Sunday**. If you’re planning to go tomorrow, just check what day it is and you’ll know whether it’s open. Enjoy your workout! ????‍♂️????️‍♀️', 'KNIGHT v1.0', '2026-10-17 15:59:23.665647', 43),
(277, 'user', 'what is the core values of kcc?', '', '2026-10-17 15:59:44.109866', 43),
(278, 'assistant', 'The core values of KCC are:\n\n1. **Kindness** – unity, empathy, and mutual support.  \n2. **Christ‑Centeredness** – living faith guided by Gospel values.  \n3. **Creativity** – innovation and problem‑solving for the Church and society.  \n4. **Integrity** – moral responsibility and academic honesty.  \n5. **Accountability** – ownership of decisions and responsible contribution.  \n6. **Nurturing** – stewardship of God’s creation.  \n7. **Synodality** – collaboration and active participation in the mission of the Church and community.', 'KNIGHT v1.0', '2026-10-17 15:59:46.052129', 43);

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(7, 'accounts', 'user'),
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(8, 'chat', 'conversation'),
(11, 'chat', 'knowledgecategory'),
(12, 'chat', 'knowledgeitem'),
(9, 'chat', 'message'),
(4, 'contenttypes', 'contenttype'),
(6, 'info', 'info'),
(5, 'sessions', 'session'),
(10, 'users', 'user');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(22, 'contenttypes', '0001_initial', '2026-10-13 03:09:53.677832'),
(23, 'contenttypes', '0002_remove_content_type_name', '2026-10-13 03:09:53.684440'),
(24, 'auth', '0001_initial', '2026-10-13 03:09:53.688662'),
(25, 'auth', '0002_alter_permission_name_max_length', '2026-10-13 03:09:53.698686'),
(26, 'auth', '0003_alter_user_email_max_length', '2026-10-13 03:09:53.706152'),
(27, 'auth', '0004_alter_user_username_opts', '2026-10-13 03:09:53.712711'),
(28, 'auth', '0005_alter_user_last_login_null', '2026-10-13 03:09:53.717347'),
(29, 'auth', '0006_require_contenttypes_0002', '2026-10-13 03:09:53.721631'),
(30, 'auth', '0007_alter_validators_add_error_messages', '2026-10-13 03:09:53.725160'),
(31, 'auth', '0008_alter_user_username_max_length', '2026-10-13 03:09:53.729043'),
(32, 'auth', '0009_alter_user_last_name_max_length', '2026-10-13 03:09:53.735313'),
(33, 'auth', '0010_alter_group_name_max_length', '2026-10-13 03:09:53.739234'),
(34, 'auth', '0011_update_proxy_permissions', '2026-10-13 03:09:53.742859'),
(35, 'auth', '0012_alter_user_first_name_max_length', '2026-10-13 03:09:53.746952'),
(36, 'users', '0001_initial', '2026-10-13 03:09:53.751129'),
(37, 'admin', '0001_initial', '2026-10-13 03:09:53.755151'),
(38, 'admin', '0002_logentry_remove_auto_add', '2026-10-13 03:09:53.758832'),
(39, 'admin', '0003_logentry_add_action_flag_choices', '2026-10-13 03:09:53.762963'),
(40, 'sessions', '0001_initial', '2026-10-13 03:09:53.768588'),
(41, 'chat', '0001_initial', '2026-10-16 13:46:02.450217'),
(42, 'chat', '0002_conversation_engine_preference_conversation_language', '2026-10-16 13:58:57.593305'),
(43, 'chat', '0003_remove_knowledgeitem_category_and_more', '2026-10-16 14:28:15.294019'),
(44, 'chat', '0004_alter_conversation_engine_preference', '2026-10-17 11:29:12.971908'),
(45, 'users', '0002_user_is_permanently_deactivated', '2026-10-17 12:27:23.617334');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('0bed1fsu2xnxvu6eeykxkc3gyxxd1wmg', '.eJxVjDEOwjAMAP_iGUW0jRPckb1vqBzbkAJqpKadEH9HlTrAene6N4y8rXncqi3jpNADwemXJZanzbvQB8_34qTM6zIltyfusNUNRe11Pdq_QeaaoQdsyFgTtqIskSigaGdIrCkYmgVhEi92iV2MaP6GTYtnjGbUeu4ifL4TwjiH:1xHift:pLdi1U2FTCp6W8iEh0SdodvCl0ND8uot3-p7BbODH18', '2026-10-30 14:12:45.214168'),
('0sau5216q3tx17rot8o3livquz4z2s1v', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSJy:0XasWos6Cd8gnLJr3An5VwC84P18wXsDKGdXsU1BW5w', '2026-10-27 02:32:54.345272'),
('19ds16m57qf1xdgqidpeeqbg13foqsae', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSwD:bCCTZuv0cboqQBcMNiY_wKO8GtScfeyB-4HIyelMJQw', '2026-10-27 03:12:25.222173'),
('2ejvwxncz1p24oia1v28blutchxb0x62', '.eJxVjEEOwiAQAP-yZ0OAslB69O4bml1YpGrapLQn499Nkx70OjOZN4y0b3Xcm6zjlGEA6-DyC5nSU-bD5AfN90WlZd7WidWRqNM2dVuyvK5n-zeo1CoM0JWe0Uoy6G0Q0lKceE1kkG3QLkZMTBgSY1eyNiERWuN9X3KJ7HWEzxcQUDgy:1xI2dR:-25gAL3bW0VImUkOBu4zDWzVOxZmyC93KUFhM-uI6xM', '2026-10-31 11:31:33.084349'),
('2g5awh4kw0jzy59f5opueylqngmeik75', '.eJxVjDEOgzAMAP_iuYogMZAyducNkWM7DW0VJAJT1b9XSAztene6NwTatxz2qmuYBUZoHVx-YSR-ajmMPKjcF8NL2dY5miMxp61mWkRft7P9G2SqGUZw1HvUVtihR-RuiKxJxSImdI1gw73vCFPylqNcVQUJxZLH5CwPFj5fGzo4xQ:1xHixa:136Q86VDAXu9l_ge9vvhA0r8iC1KkL5Fq0f00UVRRcs', '2026-10-30 14:31:02.752450'),
('2jf5k1scum2ce70d3aszoei502u3i9xj', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSvd:iAo1fcFE4TnISJ_CrsMOOR6tLUVzJyR5_Rs5OFx4JuU', '2026-10-27 03:11:49.530796'),
('3c1l17t9nublwhofh5yd8o5sgbsljb1g', '.eJxVjDkOwjAQAP-yNbLWTtZHSnreYK2P4ACypTipEH9HkVJAOzOaN3jet-L3nle_JJhAwuWXBY7PXA-RHlzvTcRWt3UJ4kjEabu4tZRf17P9GxTuBSaIMrtBoZ61StalYFw0xGgiEWZJLNGNirTUg80xWbQzMjoaKKBWaiT4fAHC0DZ-:1xGR07:4d_QpsBXHjH8fo_K6rhNljQYrW2v28S0Jj7JO2PhvYo', '2026-10-27 01:08:19.260663'),
('aatmygax7kml61ve3n6i8fg17kdtzy24', '.eJxVjMsOgjAQAP9lz6ZZtm-O3v2GZtsughpIKJyM_25IOOh1ZjJvSLxvY9qbrGmq0EOHcPmFmctT5sPUB8_3RZVl3tYpqyNRp23qtlR5Xc_2bzByG6GHoQxUfQ2WnC_EBl0wjFpQMKKYnAvb4LXXxlpDuvgoURNV6lxAlAifL_opNxA:1xHivt:eoh572Q98aqyZb0gV7Sz9kLL3j4RYl-WeAlA2D32JPI', '2026-10-30 14:29:17.606495'),
('aqhriv4uhotad1p5qav3ign08p1cpvmw', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSKD:UwZzR-PRZ4XolJ9mCWjrGcRWqRniKHTgWg5Gtq7lmkU', '2026-10-27 02:33:09.127474'),
('bi2qy7wplkieqej8srvzeux1o1dlg35t', '.eJxVjMsKwjAQAP9lzxLI5rX26N1vCLt5mKq00LSn4r9LoQe9zgyzQ-RtbXHrZYljhgEILr9MOL3KdIj85OkxqzRP6zKKOhJ12q7ucy7v29n-DRr3BgNIrmLQWeu9sakShhK086FWL-aaCJGIRddQAmstCYnIluAwcUXjHXy-34k3jw:1xHiYB:UT_t_WSGsbJCuH3KBNInKFK9dTdsbnhs6HESvWOvvtg', '2026-10-30 14:04:47.325831'),
('bqbns39bdlmga6x9uqdspud7mjf5qhvk', '.eJxVjDkOwjAQAP-yNbJ8rO04JT1vsNbH4gBKpDipEH9HkVJAOzOaN0Tatxb3Xtc4FRhBIVx-YaL8rPNhyoPm-yLyMm_rlMSRiNN2cVtKfV3P9m_QqDcYwaHjMBgmZGJjFCetrURGhWHQqRAbT1X6ZHyoPviKWjpLNqdsuRDC5wsEljg-:1xHkcQ:zsca-Qh1ufXt5g80lbKZsenEbov_VpUk7PmO46eYD1k', '2026-10-30 16:17:18.858245'),
('c1rjj578qetkp0nzxgujfcmfedqpa082', '.eJxVjEEOwiAQAP-yZ0OKXZbSo_e-gSwLSNXQpLQn499Nkx70OjOZN3jet-L3llY_RxhBw-WXBZZnqoeID673RclSt3UO6kjUaZualphet7P9GxRuBUbIySYdBwzaRXYBxYo4zH1yRNZFNDwIaumCEdZEKI4Ndb3JxlK-Gg2fL_2fN-g:1xI67V:ZEsXNMm0uXcWrGMuubRDhn262prIpwRqBKjw-R9skIc', '2026-10-31 15:14:49.103889'),
('ck32tqc6htidvcpnvf7nzchzyji519us', '.eJxVjEsKwjAUAO_y1hKSpslrunTvGcL7BFOVFpp2Jd5dCl3odmaYN2Tat5r3VtY8KYzQdXD5hUzyLPNh9EHzfTGyzNs6sTkSc9pmbouW1_Vs_waVWoURCNU7Yi4pBFFE1SDOCzk7JExR2Q6csPjYE1Hw1opD7LsoUZmRAny-HdA4Ww:1xI2ZO:T5tru9oFJLTFLDPAFOk6ml_ZC4HJw3-MVhRzjnjIu8Y', '2026-10-31 11:27:22.780981'),
('ddeeiehf4ysx2qedp3d1mbtvblvp8cqy', '.eJxVjLsOgkAQAP9la3O5BeH2KO39BrIvBTWQcFAZ_92QUGg7M5k39LytQ78VX_rRoAMkOP1CYX36tBt78HSfg87TuowS9iQctoTrbP66HO3fYOAyQAeCFluqqMaUUbxOhuRnslxpLYxRNVOFtzY7JW1YTRImZ3HKsYm5gc8X-4U35g:1xI1sb:sjsis8nlFLnBdgU6b3WAunu9cQAK4PsXBHv4Jti0uKs', '2026-10-31 10:43:09.761215'),
('e6vxs3ao49qvqwn93sdqzxfndhdic7q4', '.eJxVjDkOwjAQAP-yNbLWTtZHSnreYK2P4ACypTipEH9HkVJAOzOaN3jet-L3nle_JJhAwuWXBY7PXA-RHlzvTcRWt3UJ4kjEabu4tZRf17P9GxTuBSaIMrtBoZ61StalYFw0xGgiEWZJLNGNirTUg80xWbQzMjoaKKBWaiT4fAHC0DZ-:1xGR3f:K9KfN5fG4k0pRF4CclU893MOkL66S_BOt6pXFGiPpH8', '2026-10-27 01:11:59.149094'),
('erfc1zde61dqzmhyxe4m2qii2hj1d710', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSCV:wIbYdLXyAifRbKa2ngvGmS6omXrfw3DtnwYtpRqUmmQ', '2026-10-27 02:25:11.666229'),
('ffcy97mpy1urx3vunt95jya61wfj3iav', '.eJxVjM0OwiAQBt9lz4YALaX06N1naD52QaqGJv05Gd_dNOlBrzOTedOIfSvjvqZlnIQGMh1dfmEEP1M9jDxQ77PiuW7LFNWRqNOu6jZLel3P9m9QsBYaqEf2NlqTjO5Tdpp9nxFDm4MzaLTvHAJz4yOzBOPabDubRADtETJAny8Xozjy:1xI1nq:7ngG23qficuE6t9TMY6_78qnUoWTgEqV1I9AIXjoNWQ', '2026-10-31 10:38:14.903008'),
('h15fq7ls8b6fkqeynoyur8lvps7hws3m', '.eJxVjDEKwzAMAP-iuRgUK7GdsXvfYGRLbtIWB-JkKv17CWRo17vj3hB536a4N13jLDACOrj8wsT5qfUw8uB6X0xe6rbOyRyJOW0zt0X0dT3bv8HEbYIReEgceuqKDFQ0hY5zLxSsH5AdqydLvRbJ6MQ7X1yhhF1gS-QwI1r4fAEfFDgW:1xI1oA:-aOjsAhjlve13bSk8uqNAcWFfJ01VZvFVaOpShsDbo8', '2026-10-31 10:38:34.686303'),
('h6wdat46ay702udjn9hrle4hz7wjiayn', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSKT:iucQq76WKUIaV03iHhbhtblD83eFeNnNLdqY4uyDKbQ', '2026-10-27 02:33:25.344857'),
('igjnwibrn4b6re93mxaif3c72k0vsmhi', '.eJxVjLsOgzAMAP_FcxXhOEDM2L3fgOw4KbQVSDymqv9eITG0693p3tDLvg39vualHw068AiXX6iSnnk6jD1kus8uzdO2jOqOxJ12dbfZ8ut6tn-DQdYBOuCEgamEyMVi05j3VSyhwqZW8lizUluHxJVEDogqZqwkRuqR2kgCny_cWDcW:1xI25s:rGO0WFEZCvRJsEVHmFQFW4c0Eyl2Nvo6-tCJmQHcImw', '2026-10-31 10:56:52.844934'),
('ip3hau8fm9z1k11ircdhwmjmucinoxrb', '.eJxVjDkOwjAQAP-yNbLsjc-U9LzB8rHGAWRLcVIh_o4ipYB2ZjRv8GHfqt8HrX7JMIOByy-LIT2pHSI_Qrt3lnrb1iWyI2GnHezWM72uZ_s3qGFUmCFwi6pIzVOMxmkUZLNAE6zLBp2MmstJKU1oi0SVUpECBcnopuTUlAk-X8VnNyE:1xHiSm:7lh4W1GaEX4vz368kFdzCCR5hFSVKEA58TrPS_zBPj0', '2026-10-30 13:59:12.537068'),
('jlnvfvnva5atphi5nunl04ytb1udyald', '.eJxVjDsOwyAQBe-ydYQwC-vgMr3PgJaPg5MIJGNXUe4eIblIyjczem9wfOzZHS1tbo0wwWDh8gs9h2cq3cQHl3sVoZZ9W73oiThtE3ON6XU727-DzC3DBIm0QSsD66tFbxUuyGOg0SolByRjFkmsEb0mTTYkpjh4bfpgJTHA5wvZwja7:1xI1sr:gQnjUQ95XjkzkdAVFI0_Hi60F-HUq8yOqqKFJO6dEyM', '2026-10-31 10:43:25.658396'),
('k35utexpxp34zur0kd7n1c1m9io4gix8', '.eJxVjLsOwjAMAP_FM4rSpkncjux8Q2QnNimgVupjQvw7qtQB1rvTvSHRvtW0r7KkscAAAS6_jCk_ZTpEedB0n02ep20Z2RyJOe1qbnOR1_Vs_waV1goDMAbnFaPvgnPK2Ktlx45yUeptT5pb9KFpFLtWSucsKyPaGEUkaEb4fAHoLzhR:1xHiIS:s14mvR7en185kNyLLb2GNWC7_vh1yRF-E2LvWM2sn0M', '2026-10-30 13:48:32.341123'),
('kxc7ftbkj0em8f67dzs34xvvlh9ucoxe', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSLi:_kgstk1Ttz6r5hyMKO45BY6170jVIKnzaAUCCjA2bHo', '2026-10-27 02:34:42.157496'),
('m3doaqi0tde61sydxmd6y0u1ypzq53ks', '.eJxVjDkOwjAQAP-yNbLs9RE7JT1viLzeNQ6gRMpRIf6OIqWAdmY0bxjyvrVhX2UZRoYeHFx-GeXylOkQ_MjTfVZlnrZlJHUk6rSrus0sr-vZ_g1aXhv0kHJCtDEgBud1ClRsCpy4CkdxGDkQ6eo76XRlHdAXQeMNWSPRFirw-QLKJzeu:1xHiHb:WaF4KV6mwRGUE4RtPA9IfucObqvNTIdt6Q0O7FiThrA', '2026-10-30 13:47:39.819832'),
('noa5runjj7padq7uk3x8rcobuko94urt', '.eJxVjDEOgzAMAP_iuYpCnABm7N43IMc2hbYCicBU9e8VEkO73p3uDT3v29jvxdZ-UuggIFx-YWZ52nwYffB8X5ws87ZO2R2JO21xt0XtdT3bv8HIZYQOhKKgxgE1E1WEtbQcB84-cFJDTx6lTlg1SZJYSpilDdJoRRQjW4DPFw9fOAc:1xI2bE:ytVENXGqYh_XKtuGI7nDZ2Ep-ORag01DpEW4yfjV2sg', '2026-10-31 11:29:16.779235'),
('p87mhkblsonnyb8cvcbj5iuc0lce0ur7', '.eJxVjEEKwyAQAP-y5yJxFWNy7L1vkHVda9piICan0r8XIYf2OjPMGwIdewlHky0sCWbQCJdfGImfUrtJD6r3VfFa922JqifqtE3d1iSv69n-DQq1AjMgepssIekxm6zRSDbeZxycYBQ2dtKOjXYcMw8xshVHvlMrY5rQwecLANg3_A:1xHixY:qM134811C8pW_QTygwOVsPpUIrDYtb8pjT31Tbienmo', '2026-10-30 14:31:00.578964'),
('px20davmc86r08dsknhsbcrxbo8d2phr', '.eJxVjDEOwjAMRe_iGUWOG0joyN4zVHYS0wJKpaadEHdHkTrA-N97-m8Yed-mca95HecEPRDC6RcKx2cuzaQHl_ti4lK2dRbTEnPYaoYl5dftaP8OJq4T9MDCGIi8qD0j-kiujaCMlh0SInsblKIT1wVGScqBVFE7b_XSXeHzBfKaN6U:1xI1xr:hdZncJJ45DhkveIMIKg_DZ-Kyyk7DsTG3BjH-Dwio3k', '2026-10-31 10:48:35.254478'),
('rldzw6s3kdiwybnnng669tkabevq1k7t', '.eJxVjM0KwjAQBt9lzxJok2yTHr37DGU3-WqqkkJ_TuK7S6EHvc4M86ZB9q0M-4plmDL15Onyy1TSE_UQ-SH1Pps0122Z1ByJOe1qbnPG63q2f4Mia6GeWLQNcQwWjYfzkE7ZwUYgA46R4Dz7hpFiaDPYQ0OnFo200bKO9PkCAdg4uA:1xHiI8:XLQTeJLRVOhqYlVAfIiQES-HL_DsN0fk-LMp8X3ZNAU', '2026-10-30 13:48:12.264094'),
('rtkrpyuduiv75kiiiyuzif5y21o8xde5', '.eJxVjDEOgzAMAP_iuYogJDVm7M4bosR2Cm1FJAJT1b9XSAztene6N4S4b1PYq65hFhjAIlx-YYr81OUw8ojLvRguy7bOyRyJOW01YxF93c72bzDFOsEAhJGYiai7CreOG0ZLKo132hA6tJk8o3rKPrmUuyyabO_IK3ZtTwqfLwhrOBE:1xI6er:WmwScho3f_m_fsJF-qfnECPbfhWhZWml3zAgdCUOYzw', '2026-10-31 15:49:17.093029'),
('s2rykmmc05ift4n4wx851dksii803k18', '.eJxVjMsOwiAQAP9lz4YsdKHYo_d-QwPLIlUDSR8n47-bJj3odWYyb5jCvpVpX2WZ5gQDdHD5ZTHwU-oh0iPUe1Pc6rbMUR2JOu2qxpbkdTvbv0EJa4EBRCwb7Cm6jBx0ZEYyWTuN1yQadSJEyy77rpNeiBIRebJRe8zovYHPF-IsNyg:1xHiHK:Q3b-j2VrnN_22SFh5TqJc04i0Mmljw5m146VG0ujjqE', '2026-10-30 13:47:22.593942'),
('sqqxsl591s3naw19fzq39y05ra8hv0md', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSRZ:rgzSrX03tnQbIMLDIFtqR696SzypRzyAuCfd8zO_r4s', '2026-10-27 02:40:45.631887'),
('tpbqj4bfslh3gw5rm8qei7ao5op32grq', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSzN:MwNSWIX-SUTuXeIzXO5vZhLSLhA3vyiyEAFRKhygnzc', '2026-10-27 03:15:41.344742'),
('w610qr9361r36lj00ss0jsozanweiqte', '.eJxVjDkOwjAQAP-yNbLW8ZmU9LwhWh-LA8iW4qRC_B1FSgHtzGjeMNO-lXnveZ2XBBNIuPyyQPGZ6yHSg-q9idjqti5BHIk4bRe3lvLrerZ_g0K9wATZW2PYRjfQMOKogtVktWdmRB3YB8ZAyhE6Kz1GjyYxGxOVU45UlvD5AtphN6Y:1xGSur:fS1PMj53Lt44G6JQpoZcQ4CZqIZvqTc65Ap3mdADsoQ', '2026-10-27 03:11:01.792708'),
('xo35m4vj4k6mowstcbq9zl8dyny6e0dd', '.eJxVjDEOwjAMRe-SGUUtdpyUkZ0zVI7j0AJKpKadEHdHlTrA-t97_21G3tZp3Jou45zMxfTOnH7HyPLUspP04HKvVmpZlznaXbEHbfZWk76uh_t3MHGb9jq4rMpM2GcFiUpd5xwiBeLB9wk69ojgQMkPXgKAUNYYkATxnMF8vg3GN7k:1xI1nb:wwGzEVSFlZrl4acuad3i_VK9n07cv2t8DadrKamtkPY', '2026-10-31 10:37:59.255586'),
('zdp74xhjexq6hm3xxd3d5nf22ob6dg11', '.eJxVjEEOwiAQAP-yZ0Ngha706N03EGAXqRqalPZk_Ltp0oNeZybzhhC3tYatyxImhhHQwekXppif0nbDj9jus8pzW5cpqT1Rh-3qNrO8rkf7N6ixVxjB-JS1M6QleUvkzTA4tlqKRkOGkHI6Zy2MUhgzki_WCdsoZC7ssMDnC-14N9k:1xI2g7:N1i0H5gJSEnkCzI4cbjQcKU0SW06wYgQAa5wECy6fg0', '2026-10-31 11:34:19.136867');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `auth_user`
--
ALTER TABLE `auth_user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  ADD KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  ADD KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `chat_conversation`
--
ALTER TABLE `chat_conversation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chat_conversation_user_id_15357b84_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `chat_message`
--
ALTER TABLE `chat_message`
  ADD PRIMARY KEY (`id`),
  ADD KEY `chat_message_conversation_id_a1207bf4_fk_chat_conversation_id` (`conversation_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- AUTO_INCREMENT for table `auth_user`
--
ALTER TABLE `auth_user`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `chat_conversation`
--
ALTER TABLE `chat_conversation`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=44;

--
-- AUTO_INCREMENT for table `chat_message`
--
ALTER TABLE `chat_message`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=279;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `auth_user_groups`
--
ALTER TABLE `auth_user_groups`
  ADD CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `auth_user_user_permissions`
--
ALTER TABLE `auth_user_user_permissions`
  ADD CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `chat_conversation`
--
ALTER TABLE `chat_conversation`
  ADD CONSTRAINT `chat_conversation_user_id_15357b84_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

--
-- Constraints for table `chat_message`
--
ALTER TABLE `chat_message`
  ADD CONSTRAINT `chat_message_conversation_id_a1207bf4_fk_chat_conversation_id` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversation` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
