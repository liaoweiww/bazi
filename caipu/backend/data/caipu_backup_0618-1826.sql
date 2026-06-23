-- MySQL dump 10.13  Distrib 9.6.0, for macos26.4 (arm64)
--
-- Host: localhost    Database: caipu_app
-- ------------------------------------------------------
-- Server version	9.6.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '4ba11cf6-6624-11f1-834f-0a61c9cda6da:1-1704';

--
-- Table structure for table `checkins`
--

DROP TABLE IF EXISTS `checkins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `checkins` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记录唯一标识',
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '用户ID',
  `checkin_date` date NOT NULL COMMENT '打卡日期',
  `streak_count` int DEFAULT '1' COMMENT '连续打卡天数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '打卡时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `checkins_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='每日打卡记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `checkins`
--

LOCK TABLES `checkins` WRITE;
/*!40000 ALTER TABLE `checkins` DISABLE KEYS */;
/*!40000 ALTER TABLE `checkins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feast_menu_dishes`
--

DROP TABLE IF EXISTS `feast_menu_dishes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feast_menu_dishes` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记录唯一标识',
  `menu_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属宴席菜单ID',
  `recipe_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '菜品ID',
  `feast_category` enum('cold','hot_meat','hot_veg','soup','staple','dessert') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '宴席分类：凉菜/热荤/热素/汤羹/主食/甜品',
  `sort_order` int DEFAULT '0' COMMENT '上菜排序',
  PRIMARY KEY (`id`),
  KEY `menu_id` (`menu_id`),
  KEY `recipe_id` (`recipe_id`),
  CONSTRAINT `feast_menu_dishes_ibfk_1` FOREIGN KEY (`menu_id`) REFERENCES `feast_menus` (`id`) ON DELETE CASCADE,
  CONSTRAINT `feast_menu_dishes_ibfk_2` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='宴席菜品子表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feast_menu_dishes`
--

LOCK TABLES `feast_menu_dishes` WRITE;
/*!40000 ALTER TABLE `feast_menu_dishes` DISABLE KEYS */;
INSERT INTO `feast_menu_dishes` VALUES ('fd_1eebefc97b','fm_46181804a9','rec_3817349f4e','hot_meat',3),('fd_237abd4654','fm_2dcf2b703e','rec_dbdc9b452c','hot_meat',1),('fd_2bb9c9b6aa','fm_2dcf2b703e','rec_1b0b170448','hot_meat',0),('fd_34265e233c','fm_2dcf2b703e','rec_3817349f4e','hot_meat',4),('fd_3a9ffd172c','fm_2dcf2b703e','rec_129c0cc024','hot_meat',5),('fd_43b2f849ad','fm_46181804a9','rec_dbdc9b452c','hot_meat',1),('fd_467a31e97b','fm_46181804a9','rec_8281cf20c6','hot_meat',0),('fd_4c8fd5a7d2','fm_e8b0cb5078','rec_6e440a1876','hot_meat',5),('fd_527c705988','fm_e8b0cb5078','rec_dbdc9b452c','hot_meat',2),('fd_68a7f78f6a','fm_46181804a9','rec_1b0b170448','hot_meat',4),('fd_796db3396f','fm_46181804a9','rec_0d0a17ef8c','hot_meat',5),('fd_86c44eccae','fm_e8b0cb5078','rec_cfe35aa5b9','hot_meat',3),('fd_8b51b8582f','fm_e8b0cb5078','rec_5da0bd0274','hot_meat',1),('fd_9451d446db','fm_e8b0cb5078','rec_8281cf20c6','hot_meat',0),('fd_a8e1b8e5e3','fm_e8b0cb5078','rec_1b0b170448','hot_meat',4),('fd_b459d848c7','fm_2dcf2b703e','rec_5da0bd0274','hot_meat',3),('fd_d8e691dfdf','fm_46181804a9','rec_5da0bd0274','hot_meat',2),('fd_e459474dbb','fm_2dcf2b703e','rec_0d0a17ef8c','hot_meat',2);
/*!40000 ALTER TABLE `feast_menu_dishes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feast_menus`
--

DROP TABLE IF EXISTS `feast_menus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feast_menus` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜单唯一标识',
  `tenant_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属家庭',
  `name` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '宴席名称',
  `template_type` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '模板类型：家常小聚/双人简餐/节日正餐/多人宴席/年夜饭',
  `scene` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '宴席场景',
  `servings` int DEFAULT '6' COMMENT '宴席人数',
  `event_date` date DEFAULT NULL COMMENT '宴席日期',
  `total_cost` decimal(10,2) DEFAULT NULL COMMENT '预估总花费',
  `created_by` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '创建者userId',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `feast_menus_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE SET NULL,
  CONSTRAINT `feast_menus_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='宴席菜单表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feast_menus`
--

LOCK TABLES `feast_menus` WRITE;
/*!40000 ALTER TABLE `feast_menus` DISABLE KEYS */;
INSERT INTO `feast_menus` VALUES ('fm_2dcf2b703e','test_tenant','随机一桌 2026/6/16',NULL,'',6,NULL,NULL,NULL,'2026-06-16 20:08:39','2026-06-16 20:08:39'),('fm_46181804a9','test_tenant','随机一桌 2026/6/16',NULL,'elders',6,NULL,NULL,NULL,'2026-06-16 20:08:49','2026-06-16 20:08:49'),('fm_e8b0cb5078','test_tenant','随机一桌 2026/6/16',NULL,'',6,NULL,NULL,NULL,'2026-06-16 20:08:46','2026-06-16 20:08:46');
/*!40000 ALTER TABLE `feast_menus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ingredients`
--

DROP TABLE IF EXISTS `ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredients` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '食材唯一标识',
  `name` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '食材名称',
  `emoji` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '食材emoji图标',
  `image` text COLLATE utf8mb4_unicode_ci,
  `category1` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '一级分类：畜禽肉类/鲜蔬类/水产海鲜/五谷干货/调味佐料/水果类',
  `category2` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '二级分类：猪肉类/绿叶蔬菜/淡水鱼等',
  `category3` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `unit` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT '斤' COMMENT '默认单位',
  `storage` enum('fridge','freezer','room') COLLATE utf8mb4_unicode_ci DEFAULT 'room' COMMENT '储存方式：冷藏/冷冻/常温',
  `shelf_life_days` int DEFAULT NULL COMMENT '建议存放天数（冷藏/冷冻类）',
  `reference_price` decimal(8,2) DEFAULT NULL,
  `is_system` tinyint(1) DEFAULT '1' COMMENT '是否系统预设（不可删除）',
  `created_by` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '自定义食材的创建者userId',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `ingredients_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食材库表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredients`
--

LOCK TABLES `ingredients` WRITE;
/*!40000 ALTER TABLE `ingredients` DISABLE KEYS */;
INSERT INTO `ingredients` VALUES ('ing_almond','杏仁','🥜',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_amaranth','苋菜','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',2,3.50,1,NULL),('ing_apple','苹果','🍎',NULL,'水果类','常见水果','常见水果','斤','fridge',14,6.00,1,NULL),('ing_baby_cabbage','娃娃菜','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,3.00,1,NULL),('ing_baby_pumpkin','贝贝南瓜','🎃',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','room',NULL,3.00,1,NULL),('ing_bamboo_fungus','竹荪','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','room',NULL,20.00,1,NULL),('ing_banana','香蕉','🍌',NULL,'水果类','常见水果','常见水果','斤','room',NULL,4.00,1,NULL),('ing_basa','巴沙鱼','🐟',NULL,'水产海鲜','海鱼','海鱼','斤','freezer',60,14.00,1,NULL),('ing_bass','鲈鱼','🐟',NULL,'水产海鲜','淡水鱼','淡水鱼','斤','fridge',2,16.00,1,NULL),('ing_bay_leaf','香叶','🌿',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_bean_paste','豆瓣酱','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,8.00,1,NULL),('ing_beech_mush','蟹味菇','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','fridge',5,8.00,1,NULL),('ing_beef_brisket','牛腩','🐮',NULL,'畜禽肉类','畜肉','牛','斤','fridge',3,35.00,1,NULL),('ing_beef_eye','牛里脊','🥩',NULL,'畜禽肉类','畜肉','牛','斤','fridge',3,40.00,1,NULL),('ing_beef_omasum','牛百叶','🐮',NULL,'畜禽肉类','畜肉','牛','斤','fridge',2,28.00,1,NULL),('ing_beef_rib','牛肋条','🐮',NULL,'畜禽肉类','畜肉','牛','斤','fridge',3,36.00,1,NULL),('ing_beef_shank','牛腱子','🐮',NULL,'畜禽肉类','畜肉','牛','斤','fridge',3,38.00,1,NULL),('ing_beef_slice','牛肉片','🥩',NULL,'畜禽肉类','畜肉','牛','斤','fridge',3,35.00,1,NULL),('ing_beef_tallow','牛油','🥩',NULL,'调味佐料','油脂','油脂类','斤','fridge',30,8.00,1,NULL),('ing_beef_tongue','牛舌','🐮',NULL,'畜禽肉类','畜肉','牛','斤','fridge',2,45.00,1,NULL),('ing_bitter_gourd','苦瓜','🥒',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','fridge',5,3.00,1,NULL),('ing_black_bean','黑豆','🫘',NULL,'五谷干货','豆类','豆类杂粮','斤','room',NULL,6.00,1,NULL),('ing_black_pepper','黑胡椒粉','🧂',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_black_rice','黑米','🍚',NULL,'五谷干货','主食','主食谷物','斤','room',NULL,3.00,1,NULL),('ing_bokchoy','上海青','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,3.50,1,NULL),('ing_broccoli','西兰花','🥦',NULL,'鲜蔬类','香辛','香辛配菜','斤','fridge',5,4.00,1,NULL),('ing_brown_rice','糙米','🍚',NULL,'五谷干货','主食','主食谷物','斤','room',NULL,3.00,1,NULL),('ing_brown_sugar','红糖','🍬',NULL,'调味佐料','基础调味','基础调味','斤','room',NULL,2.00,1,NULL),('ing_carrot','胡萝卜','🥕',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','fridge',7,2.00,1,NULL),('ing_catfish','鲶鱼','🐟',NULL,'水产海鲜','淡水鱼','淡水鱼','斤','fridge',2,12.00,1,NULL),('ing_cauliflower','花菜','🥦',NULL,'鲜蔬类','香辛','香辛配菜','斤','fridge',5,4.00,1,NULL),('ing_celery','芹菜','🥬',NULL,'鲜蔬类','香辛','香辛配菜','斤','fridge',5,4.00,1,NULL),('ing_celtuce','莴笋','🥬',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','fridge',5,2.50,1,NULL),('ing_century_egg','皮蛋','🥚',NULL,'畜禽肉类','蛋类','皮蛋','个','room',NULL,6.50,1,NULL),('ing_cherry','樱桃','🍒',NULL,'水果类','常见水果','常见水果','斤','fridge',5,8.00,1,NULL),('ing_chicken_breast','鸡胸肉','🐔',NULL,'畜禽肉类','禽肉','鸡','斤','fridge',2,12.00,1,NULL),('ing_chicken_essence','鸡精','🧂',NULL,'调味佐料','基础调味','基础调味','斤','room',NULL,2.00,1,NULL),('ing_chicken_leg','鸡腿','🍗',NULL,'畜禽肉类','禽肉','鸡','斤','fridge',2,10.00,1,NULL),('ing_chicken_whole','整鸡','🐔',NULL,'畜禽肉类','禽肉','鸡','斤','fridge',2,12.00,1,NULL),('ing_chicken_wing','鸡翅','🍗',NULL,'畜禽肉类','禽肉','鸡','斤','fridge',2,14.00,1,NULL),('ing_chickpea','鹰嘴豆','🫘',NULL,'五谷干货','豆类','豆类杂粮','斤','room',NULL,6.00,1,NULL),('ing_chili_oil','辣椒油','🌶️',NULL,'调味佐料','油脂','油脂类','毫升','room',NULL,15.00,1,NULL),('ing_chili_sauce','辣椒酱','🌶️',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,10.00,1,NULL),('ing_chive','韭菜','🌿',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',2,3.50,1,NULL),('ing_choi_sum','菜心','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,3.50,1,NULL),('ing_cilantro','香菜','🌿',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,4.00,1,NULL),('ing_cinnamon','桂皮','🪵',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_clam','花甲','🦪',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,35.00,1,NULL),('ing_clams','花蛤','🦪',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,8.00,1,NULL),('ing_cod','鳕鱼','🐟',NULL,'水产海鲜','海鱼','海鱼','斤','freezer',60,25.00,1,NULL),('ing_cooking_oil','食用油','🫒',NULL,'调味佐料','油脂','油脂类','毫升','room',NULL,12.00,1,NULL),('ing_cooking_wine','料酒','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,6.00,1,NULL),('ing_corn','玉米','🌽',NULL,'五谷干货','主食','主食谷物','斤','room',NULL,3.00,1,NULL),('ing_crab','螃蟹','🦀',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,35.00,1,NULL),('ing_crayfish','小龙虾','🦞',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,35.00,1,NULL),('ing_crown_daisy','茼蒿','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',2,3.50,1,NULL),('ing_crucian_carp','鲫鱼','🐟',NULL,'水产海鲜','淡水鱼','淡水鱼','斤','fridge',2,12.00,1,NULL),('ing_cucumber','黄瓜','🥒',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','fridge',5,2.50,1,NULL),('ing_cumin','孜然','🌿',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_custom_00bc74aa','00','📦','/uploads/12a9a3d5342241c5a467a97d2d2dcb77.png','水果类','常见水果',NULL,'20斤','room',NULL,NULL,0,NULL),('ing_custom_047ebc1f','2','📦','','鲜蔬类','自定义',NULL,'适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_0a38d5cc','蒜苗','📦',NULL,'鲜蔬类','自定义','自定义','克','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_0ac751a8','牛肉粒','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_0c68dd13','蒜苗','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_132439a0','嫩豆腐','🥒',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_2a8a5cc5','牛肉','🥩',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_39480a15','蒜苗','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_3cf6f3cf','牛肉','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_475f2af8','豆豉','🥒',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_4eab9b2b','五花肉','📦',NULL,'鲜蔬类','自定义','自定义','克','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_50d0502a','五花肉','🥩',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_606e6d1a','蒜苗','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_60eadde0','蒜苗','🥬',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_6a9e96c7','蒜苗','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_8577f4b7','蒜苗','🥬',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_8948920e','牛肉','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_95ad4acc','五花肉','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_a3f309a6','蒜苗','📦',NULL,'鲜蔬类','自定义','自定义','根','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_ac52e4ad','牛肉','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_acbd0196','五花肉','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_ad01637b','蒜苗','📦',NULL,'鲜蔬类','自定义','自定义','克','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_b36abe6a','五花肉','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_bad8a2c1','五花肉','🥩',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_beef','牛肉','🥩',NULL,'畜禽肉类','自定义','自定义','克','fridge',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_dcdcfb39','2222','📦','/uploads/1039715bef5e41f2be85a719e132945d.png','水果类','自定义',NULL,'斤','room',NULL,NULL,0,NULL),('ing_custom_e13ee3dc','五花肉','📦',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_e1d5324b','蒜苗','🥬',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_f4810db4','五花肉','📦',NULL,'鲜蔬类','自定义','自定义','克','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_custom_f5582e9c','猪肉','🥩',NULL,'鲜蔬类','自定义','自定义','适量','room',NULL,NULL,0,'wx_bzlqzuagcb'),('ing_cuttlefish','墨鱼','🦑',NULL,'水产海鲜','其他水产','其他水产','斤','freezer',60,NULL,1,NULL),('ing_dark_soy','老抽','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,8.00,1,NULL),('ing_dragon_fruit','火龙果','🐉',NULL,'水果类','常见水果','常见水果','斤','room',NULL,8.00,1,NULL),('ing_dried_chili','干辣椒','🌶️',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_dried_noodle','挂面','🍜',NULL,'五谷干货','面食','面食干货','斤','room',NULL,5.00,1,NULL),('ing_dried_scallop','干贝','🦪',NULL,'水产海鲜','其他水产','其他水产','斤','room',NULL,NULL,1,NULL),('ing_dried_shrimp','虾米','🦐',NULL,'水产海鲜','其他水产','其他水产','斤','room',NULL,NULL,1,NULL),('ing_duck','鸭肉','🦆',NULL,'畜禽肉类','禽肉','鸭','斤','fridge',2,15.00,1,NULL),('ing_duck_egg','鸭蛋','🥚',NULL,'畜禽肉类','蛋类','鸭蛋','个','room',NULL,8.00,1,NULL),('ing_duck_leg','鸭腿','🦆',NULL,'畜禽肉类','禽肉','鸭','斤','fridge',2,16.00,1,NULL),('ing_duck_neck','鸭脖','🦆',NULL,'畜禽肉类','禽肉','鸭','斤','fridge',2,16.00,1,NULL),('ing_duck_wing','鸭翅','🦆',NULL,'畜禽肉类','禽肉','鸭','斤','fridge',2,16.00,1,NULL),('ing_egg','鸡蛋','🥚',NULL,'畜禽肉类','蛋类','鸡蛋','个','room',NULL,6.00,1,NULL),('ing_eggplant','茄子','🍆',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','fridge',5,3.00,1,NULL),('ing_enoki','金针菇','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','fridge',5,5.00,1,NULL),('ing_fennel','小茴香','🌿',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_fragrant_vinegar','香醋','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,8.00,1,NULL),('ing_garlic','大蒜','🧄',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','room',NULL,5.00,1,NULL),('ing_garlic_scape','蒜苔','🌱',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,3.50,1,NULL),('ing_garlic_sprout','蒜苗','🌱',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,5.00,1,NULL),('ing_ginger','生姜','🫚',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','room',NULL,6.00,1,NULL),('ing_glutinous_rice','糯米','🍚',NULL,'五谷干货','主食','主食谷物','斤','room',NULL,3.00,1,NULL),('ing_goji','枸杞','🔴',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_goose','鹅肉','🦢',NULL,'畜禽肉类','禽肉','鹅','斤','fridge',2,NULL,1,NULL),('ing_grape','葡萄','🍇',NULL,'水果类','常见水果','常见水果','斤','fridge',7,8.00,1,NULL),('ing_grass_carp','草鱼','🐟',NULL,'水产海鲜','淡水鱼','淡水鱼','斤','fridge',2,10.00,1,NULL),('ing_green_onion','小葱','🌱',NULL,'鲜蔬类','香辛','香辛配菜','斤','fridge',5,3.00,1,NULL),('ing_green_pepper','青椒','🫑',NULL,'鲜蔬类','香辛','香辛配菜','斤','fridge',5,4.00,1,NULL),('ing_hairtail','带鱼','🐟',NULL,'水产海鲜','海鱼','海鱼','斤','freezer',60,25.00,1,NULL),('ing_instant_noodle','方便面','🍜',NULL,'五谷干货','面食','面食干货','斤','room',NULL,5.00,1,NULL),('ing_jellyfish','海蜇','🪼',NULL,'水产海鲜','其他水产','其他水产','斤','fridge',3,NULL,1,NULL),('ing_kale_ch','芥蓝','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,3.50,1,NULL),('ing_ketchup','番茄酱','🥫',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,8.00,1,NULL),('ing_kidney_bean','芸豆','🫘',NULL,'五谷干货','豆类','豆类杂粮','斤','room',NULL,6.00,1,NULL),('ing_king_oyster','杏鲍菇','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','fridge',5,8.00,1,NULL),('ing_kiwi','猕猴桃','🥝',NULL,'水果类','常见水果','常见水果','斤','fridge',7,8.00,1,NULL),('ing_lamb_chunk','羊肉块','🐑',NULL,'畜禽肉类','畜肉','羊','斤','freezer',90,42.00,1,NULL),('ing_lamb_leg','羊腿肉','🐑',NULL,'畜禽肉类','畜肉','羊','斤','freezer',90,38.00,1,NULL),('ing_lamb_offal','羊杂','🐑',NULL,'畜禽肉类','畜肉','羊','斤','freezer',60,42.00,1,NULL),('ing_lamb_rib','羊排','🐑',NULL,'畜禽肉类','畜肉','羊','斤','freezer',90,40.00,1,NULL),('ing_lamb_slice','羊肉卷','🐑',NULL,'畜禽肉类','畜肉','羊','斤','freezer',90,42.00,1,NULL),('ing_lard','猪油','🥩',NULL,'调味佐料','油脂','油脂类','斤','fridge',30,15.00,1,NULL),('ing_leek_onion','大葱','🌱',NULL,'鲜蔬类','香辛','香辛配菜','斤','fridge',7,4.00,1,NULL),('ing_lettuce','生菜','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,2.00,1,NULL),('ing_lettuce_oil','油麦菜','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,3.50,1,NULL),('ing_light_soy','生抽','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,8.00,1,NULL),('ing_lily_bulb','百合','🌺',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_longan','桂圆','🫐',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_longan_fruit','龙眼','🫐',NULL,'水果类','常见水果','常见水果','斤','fridge',3,8.00,1,NULL),('ing_lotus_root','莲藕','🪷',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','fridge',7,5.00,1,NULL),('ing_lotus_seed','莲子','🪷',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_luffa','丝瓜','🥒',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','fridge',5,3.50,1,NULL),('ing_lychee','荔枝','🫐',NULL,'水果类','常见水果','常见水果','斤','fridge',3,8.00,1,NULL),('ing_mango','芒果','🥭',NULL,'水果类','常见水果','常见水果','斤','room',NULL,8.00,1,NULL),('ing_millet','小米','🫘',NULL,'五谷干货','主食','主食谷物','斤','room',NULL,3.00,1,NULL),('ing_msg','味精','🧂',NULL,'调味佐料','基础调味','基础调味','斤','room',NULL,2.00,1,NULL),('ing_mung_bean','绿豆','🫘',NULL,'五谷干货','豆类','豆类杂粮','斤','room',NULL,6.00,1,NULL),('ing_noodle','面条','🍜',NULL,'五谷干货','面食','面食干货','斤','room',NULL,5.00,1,NULL),('ing_oats','燕麦','🌾',NULL,'五谷干货','主食','主食谷物','斤','room',NULL,3.00,1,NULL),('ing_onion','洋葱','🧅',NULL,'鲜蔬类','香辛','香辛配菜','斤','room',NULL,2.50,1,NULL),('ing_orange','橙子','🍊',NULL,'水果类','常见水果','常见水果','斤','room',NULL,5.00,1,NULL),('ing_oyster','生蚝','🦪',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,35.00,1,NULL),('ing_oyster_mush','平菇','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','fridge',3,6.00,1,NULL),('ing_oyster_sauce','蚝油','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,10.00,1,NULL),('ing_peanut','花生','🥜',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_pear','梨','🍐',NULL,'水果类','常见水果','常见水果','斤','fridge',14,8.00,1,NULL),('ing_pigeon','鸽子肉','🐦',NULL,'畜禽肉类','禽肉','鸽','斤','fridge',2,NULL,1,NULL),('ing_pineapple','菠萝','🍍',NULL,'水果类','常见水果','常见水果','斤','room',NULL,8.00,1,NULL),('ing_pork_belly','五花肉','🥩',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,14.00,1,NULL),('ing_pork_ear','猪耳朵','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,15.00,1,NULL),('ing_pork_heart','猪心','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',2,15.00,1,NULL),('ing_pork_intestine','猪大肠','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',2,15.00,1,NULL),('ing_pork_lean','瘦肉','🥩',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,15.00,1,NULL),('ing_pork_liver','猪肝','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',2,8.00,1,NULL),('ing_pork_rib','排骨','🍖',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,18.00,1,NULL),('ing_pork_skin','猪皮','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,15.00,1,NULL),('ing_pork_tender','里脊肉','🥩',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,15.00,1,NULL),('ing_pork_tongue','猪舌头','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,15.00,1,NULL),('ing_pork_tripe','猪肚','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',2,15.00,1,NULL),('ing_pork_trotter','猪蹄','🐷',NULL,'畜禽肉类','畜肉','猪','斤','fridge',3,15.00,1,NULL),('ing_potato','土豆','🥔',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','room',NULL,1.50,1,NULL),('ing_pumpkin','南瓜','🎃',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','room',NULL,2.00,1,NULL),('ing_quail_egg','鹌鹑蛋','🥚',NULL,'畜禽肉类','蛋类','鹌鹑蛋','个','room',NULL,6.50,1,NULL),('ing_radish','白萝卜','🥕',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','fridge',7,1.50,1,NULL),('ing_razor_clam','蛏子','🦪',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,35.00,1,NULL),('ing_red_bean','红豆','🫘',NULL,'五谷干货','豆类','豆类杂粮','斤','room',NULL,6.00,1,NULL),('ing_red_date','红枣','🫒',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_red_pepper','红椒','🫑',NULL,'鲜蔬类','香辛','香辛配菜','斤','fridge',5,4.00,1,NULL),('ing_rice','大米','🍚',NULL,'五谷干货','主食','主食谷物','斤','room',NULL,3.00,1,NULL),('ing_rice_noodle','河粉','🍜',NULL,'五谷干货','面食','面食干货','斤','fridge',2,5.00,1,NULL),('ing_rice_vermicelli','米粉','🍜',NULL,'五谷干货','面食','面食干货','斤','room',NULL,5.00,1,NULL),('ing_rock_sugar','冰糖','🍬',NULL,'调味佐料','基础调味','基础调味','斤','room',NULL,6.00,1,NULL),('ing_salmon','三文鱼','🍣',NULL,'水产海鲜','海鱼','海鱼','斤','fridge',2,25.00,1,NULL),('ing_salt','食盐','🧂',NULL,'调味佐料','基础调味','基础调味','斤','room',NULL,2.00,1,NULL),('ing_salted_egg','咸鸭蛋','🥚',NULL,'畜禽肉类','蛋类','鸭蛋','个','room',NULL,6.50,1,NULL),('ing_saury','秋刀鱼','🐟',NULL,'水产海鲜','海鱼','海鱼','斤','freezer',60,25.00,1,NULL),('ing_scallion_oil','葱油','🌿',NULL,'调味佐料','油脂','油脂类','毫升','room',NULL,15.00,1,NULL),('ing_scallop','扇贝','🦪',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,35.00,1,NULL),('ing_sea_cucumber','海参','🪸',NULL,'水产海鲜','其他水产','其他水产','斤','freezer',90,NULL,1,NULL),('ing_sesame','芝麻','🫘',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_sesame_oil','香油','🫒',NULL,'调味佐料','油脂','油脂类','毫升','room',NULL,20.00,1,NULL),('ing_shiitake','香菇','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','fridge',5,12.00,1,NULL),('ing_shrimp','基围虾','🦐',NULL,'水产海鲜','虾蟹贝','虾蟹贝类','斤','fridge',2,30.00,1,NULL),('ing_sichuan_oil','花椒油','🌶️',NULL,'调味佐料','油脂','油脂类','毫升','room',NULL,15.00,1,NULL),('ing_sichuan_pepper','花椒','🌶️',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_snakehead','黑鱼','🐟',NULL,'水产海鲜','淡水鱼','淡水鱼','斤','fridge',2,12.00,1,NULL),('ing_soybean','黄豆','🫘',NULL,'五谷干货','豆类','豆类杂粮','斤','room',NULL,6.00,1,NULL),('ing_spinach','菠菜','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',3,3.00,1,NULL),('ing_squid','鱿鱼','🦑',NULL,'水产海鲜','其他水产','其他水产','斤','freezer',60,22.00,1,NULL),('ing_star_anise','八角','⭐',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_strawberry','草莓','🍓',NULL,'水果类','常见水果','常见水果','斤','fridge',3,8.00,1,NULL),('ing_sugar','白砂糖','🍬',NULL,'调味佐料','基础调味','基础调味','斤','room',NULL,5.00,1,NULL),('ing_sweet_bean','甜面酱','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,8.00,1,NULL),('ing_tangerine','橘子','🍊',NULL,'水果类','常见水果','常见水果','斤','room',NULL,8.00,1,NULL),('ing_taro','芋头','🥔',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','room',NULL,2.50,1,NULL),('ing_tea_mush','茶树菇','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','room',NULL,8.00,1,NULL),('ing_tilapia','罗非鱼','🐟',NULL,'水产海鲜','淡水鱼','淡水鱼','斤','fridge',2,12.00,1,NULL),('ing_tomato','西红柿','🍅',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','room',NULL,3.00,1,NULL),('ing_vermicelli','粉丝','🫘',NULL,'五谷干货','面食','面食干货','斤','room',NULL,5.00,1,NULL),('ing_vinegar','陈醋','🫗',NULL,'调味佐料','酱汁','酱汁调味','毫升','room',NULL,6.00,1,NULL),('ing_walnut','核桃','🥜',NULL,'五谷干货','干果','干果干货','斤','room',NULL,15.00,1,NULL),('ing_water_chestnut','马蹄','🥔',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','room',NULL,2.50,1,NULL),('ing_water_spinach','空心菜','🥬',NULL,'鲜蔬类','绿叶菜','绿叶蔬菜','斤','fridge',2,3.50,1,NULL),('ing_watermelon','西瓜','🍉',NULL,'水果类','常见水果','常见水果','斤','fridge',7,2.00,1,NULL),('ing_wax_gourd','冬瓜','🎃',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','room',NULL,3.00,1,NULL),('ing_white_beech','白玉菇','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','fridge',5,8.00,1,NULL),('ing_white_pepper','白胡椒粉','🧂',NULL,'调味佐料','香料','香料调味','两','room',NULL,12.00,1,NULL),('ing_wide_vermicelli','粉条','🫘',NULL,'五谷干货','面食','面食干货','斤','room',NULL,5.00,1,NULL),('ing_wood_ear','木耳','🍄',NULL,'鲜蔬类','菌菇','菌菇杂蔬','斤','room',NULL,15.00,1,NULL),('ing_wuchang_bream','武昌鱼','🐟',NULL,'水产海鲜','淡水鱼','淡水鱼','斤','fridge',2,12.00,1,NULL),('ing_yam','山药','🥔',NULL,'鲜蔬类','根茎','根茎蔬菜','斤','room',NULL,8.00,1,NULL),('ing_yellow_croaker','黄花鱼','🐟',NULL,'水产海鲜','海鱼','海鱼','斤','fridge',2,25.00,1,NULL),('ing_zucchini','西葫芦','🥒',NULL,'鲜蔬类','瓜茄','瓜茄果蔬','斤','fridge',5,3.00,1,NULL);
/*!40000 ALTER TABLE `ingredients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `meal_plans`
--

DROP TABLE IF EXISTS `meal_plans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `meal_plans` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记录唯一标识',
  `tenant_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属家庭',
  `plan_date` date NOT NULL COMMENT '规划日期',
  `meal_type` enum('breakfast','lunch','dinner') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '餐段：早餐/午餐/晚餐',
  `recipe_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '菜品ID',
  `servings` int DEFAULT '4' COMMENT '用餐人数',
  `created_by` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '创建者userId',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `meal_plans_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
  CONSTRAINT `meal_plans_ibfk_2` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE SET NULL,
  CONSTRAINT `meal_plans_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='点菜规划表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `meal_plans`
--

LOCK TABLES `meal_plans` WRITE;
/*!40000 ALTER TABLE `meal_plans` DISABLE KEYS */;
INSERT INTO `meal_plans` VALUES ('mp_007734ea83','test_tenant','2026-06-20','lunch','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_02ad96b2ec','test_tenant','2026-06-22','breakfast','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_02e45377ec','test_tenant','2026-06-19','breakfast','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_0927578c23','test_tenant','2026-06-21','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_10738b46b9','test_tenant','2026-06-16','lunch','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_138c18f49c','test_tenant','2026-06-22','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_13eb98c02f','test_tenant','2026-06-16','dinner','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_144c28e73a','test_tenant','2026-06-21','lunch','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_18923e8202','test_tenant','2026-06-20','lunch','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_21c9f972e7','test_tenant','2026-06-22','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:37'),('mp_259439fbdd','test_tenant','2026-06-19','dinner','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_270cd5f64b','test_tenant','2026-06-17','dinner','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_2813e48377','test_tenant','2026-06-20','dinner','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_294a87dcf2','test_tenant','2026-06-17','lunch','rec_cfe35aa5b9',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_2a5e411b62','test_tenant','2026-06-19','breakfast','rec_cfe35aa5b9',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_3044e57661','test_tenant','2026-06-17','breakfast','rec_1b0b170448',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_31538c46dc','test_tenant','2026-06-21','lunch','rec_6e440a1876',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_326f12917d','test_tenant','2026-06-17','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_3a9cf46109','test_tenant','2026-06-20','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_3c61547c5d','test_tenant','2026-06-20','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_3ddacd4b7c','test_tenant','2026-06-20','breakfast','rec_6e440a1876',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_3e387d6f30','test_tenant','2026-06-19','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_436706f322','test_tenant','2026-06-20','dinner','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_489556dffb','test_tenant','2026-06-20','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_48a4e69f1a','test_tenant','2026-06-19','breakfast','rec_1b0b170448',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_4c4452a24d','test_tenant','2026-06-22','dinner','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:37'),('mp_4cd5f25c43','test_tenant','2026-06-17','dinner','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_4d50260d7d','test_tenant','2026-06-19','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_54983c6ebd','test_tenant','2026-06-22','breakfast','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_581a4f954f','test_tenant','2026-06-22','dinner','rec_dbdc9b452c',6,'wx_bzlqzuagcb','2026-06-16 22:03:37'),('mp_5af6670f1f','test_tenant','2026-06-16','dinner','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_5c791cdecc','test_tenant','2026-06-19','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_602c460aae','test_tenant','2026-06-19','dinner','rec_dbdc9b452c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_62fbac774e','test_tenant','2026-06-21','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_66817f6f20','test_tenant','2026-06-16','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_69b9844b12','test_tenant','2026-06-19','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_6aee0af877','test_tenant','2026-06-19','lunch','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_6cbc707ce7','test_tenant','2026-06-17','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_6dfaebf7b5','test_tenant','2026-06-19','lunch','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_6eb89a1947','test_tenant','2026-06-21','lunch','rec_129c0cc024',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_6f9459468b','test_tenant','2026-06-20','breakfast','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_76d3c89079','test_tenant','2026-06-19','lunch','rec_dbdc9b452c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_7d60f80871','test_tenant','2026-06-21','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_7d9212fe3c','test_tenant','2026-06-22','dinner','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:37'),('mp_81980a7699','test_tenant','2026-06-16','lunch','rec_dbdc9b452c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_82450c513e','test_tenant','2026-06-21','dinner','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_8adc8e2236','test_tenant','2026-06-21','breakfast','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_8b7bd2a399','test_tenant','2026-06-20','breakfast','rec_6e440a1876',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_8ddbef1b47','test_tenant','2026-06-16','lunch','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_956f087905','test_tenant','2026-06-21','breakfast','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_9621c2974b','test_tenant','2026-06-21','breakfast','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_96cb93d5a6','test_tenant','2026-06-17','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_9cf8a16b46','test_tenant','2026-06-16','breakfast','rec_cfe35aa5b9',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_9f055a4196','test_tenant','2026-06-22','breakfast','rec_cfe35aa5b9',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_a4093b1dae','test_tenant','2026-06-17','breakfast','rec_6e440a1876',4,'wx_bzlqzuagcb','2026-06-17 17:56:17'),('mp_aba148b62e','test_tenant','2026-06-20','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_ac67e801fe','test_tenant','2026-06-22','lunch','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_b1619aba29','test_tenant','2026-06-17','lunch','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_b5a7e5805f','test_tenant','2026-06-16','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_b74316a5fc','test_tenant','2026-06-21','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_b77bca1a8d','test_tenant','2026-06-20','dinner','rec_6e440a1876',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_b7a3c60c36','test_tenant','2026-06-17','dinner','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_bab4fb316f','test_tenant','2026-06-16','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_c04440d99f','test_tenant','2026-06-12','lunch',NULL,4,'wx_bzlqzuagcb','2026-06-12 18:24:57'),('mp_d1ba6f70be','test_tenant','2026-06-16','dinner','rec_dbdc9b452c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_d1e3ba99b3','test_tenant','2026-06-17','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_d2d63e64a7','test_tenant','2026-06-17','breakfast','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_d60cc8e951','test_tenant','2026-06-22','lunch','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:37'),('mp_d898c82eb1','test_tenant','2026-06-22','dinner','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:37'),('mp_dab09a498c','test_tenant','2026-06-16','breakfast','rec_129c0cc024',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_db77d27f05','test_tenant','2026-06-16','lunch','rec_129c0cc024',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_db83609419','test_tenant','2026-06-16','breakfast','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_dd1ee4c62a','test_tenant','2026-06-17','lunch','rec_3817349f4e',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_dda568ac8d','test_tenant','2026-06-20','lunch','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_df32a42b09','test_tenant','2026-06-17','breakfast','rec_1b0b170448',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_e34716ad09','test_tenant','2026-06-16','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_e44a3de162','test_tenant','2026-06-21','lunch','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_e64e85108f','test_tenant','2026-06-22','lunch','rec_cfe35aa5b9',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_e8c9cabab2','test_tenant','2026-06-22','lunch','rec_5da0bd0274',6,'wx_bzlqzuagcb','2026-06-16 22:03:37'),('mp_e98c90b169','test_tenant','2026-06-22','lunch','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_eca10120ee','test_tenant','2026-06-19','lunch','rec_cfe35aa5b9',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_edf2dbb75d','test_tenant','2026-06-19','dinner','rec_0d0a17ef8c',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_ef974738c4','test_tenant','2026-06-20','lunch','rec_6e440a1876',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_f050d96134','test_tenant','2026-06-21','dinner','rec_8281cf20c6',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_f67b4e75a2','test_tenant','2026-06-17','lunch','rec_129c0cc024',6,'wx_bzlqzuagcb','2026-06-16 22:03:36'),('mp_f897bc6779','test_tenant','2026-06-21','dinner','rec_6e440a1876',6,'wx_bzlqzuagcb','2026-06-16 22:03:36');
/*!40000 ALTER TABLE `meal_plans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchases` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记录唯一标识',
  `tenant_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属家庭（家庭级数据）',
  `ingredient_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '食材ID',
  `price` decimal(8,2) DEFAULT NULL COMMENT '单价',
  `total_price` decimal(8,2) DEFAULT NULL COMMENT '总价',
  `quantity` decimal(8,2) DEFAULT NULL COMMENT '数量',
  `unit` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '购买单位',
  `purchase_date` date DEFAULT NULL COMMENT '采购日期',
  `location` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '购买地点',
  `note` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_by` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '录入者userId',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `ingredient_id` (`ingredient_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE SET NULL,
  CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE SET NULL,
  CONSTRAINT `purchases_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='采购记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
INSERT INTO `purchases` VALUES ('pur_0554a2d9d4','test_tenant','ing_pork_belly',14.00,14.00,500.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:04:54'),('pur_0610334ec2','test_tenant','ing_pork_rib',18.00,18.00,500.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:04:57'),('pur_0bd245bdbc','test_tenant','ing_orange',15.00,15.00,500.00,'g','2026-06-17','南坛菜市场',NULL,'wx_bzlqzuagcb','2026-06-17 17:26:33'),('pur_196e1d162e','test_tenant','ing_beef_omasum',28.00,11.00,196.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:01:52'),('pur_319ba0ffc0','test_tenant','ing_pork_rib',16.00,17.70,553.00,'g','2026-06-17','南坛菜市场',NULL,'wx_bzlqzuagcb','2026-06-17 17:05:08'),('pur_400d7e66f0','test_tenant','ing_pork_belly',20.00,40.00,1000.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:57:13'),('pur_6fa88c9728','test_tenant','ing_pear',8.00,8.02,501.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:26:27'),('pur_6fbe1566e7','test_tenant','ing_yam',8.00,11.00,688.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:01:48'),('pur_84220539b4','test_tenant','ing_pork_rib',19.00,19.00,500.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:05:02'),('pur_8f7f64dd40','test_tenant','ing_ginger',6.00,5.00,417.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:05:24'),('pur_ee77f0576c','test_tenant','ing_pork_belly',25.00,25.00,500.00,'g','2026-06-17','南坛菜市场',NULL,'wx_bzlqzuagcb','2026-06-17 17:01:42'),('pur_f45ee52c39','test_tenant','ing_pork_belly',19.50,30.00,769.00,'g','2026-06-17','南坛菜市场','','wx_bzlqzuagcb','2026-06-17 17:55:59');
/*!40000 ALTER TABLE `purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipe_ingredients`
--

DROP TABLE IF EXISTS `recipe_ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recipe_ingredients` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记录唯一标识',
  `recipe_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属菜谱ID',
  `ingredient_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '食材ID',
  `amount` decimal(8,2) DEFAULT NULL COMMENT '用量数值',
  `unit` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '单位：克/毫升/个/勺/根',
  `is_staple` tinyint(1) DEFAULT '0' COMMENT '是否主食（换算基准）',
  `sort_order` int DEFAULT '0' COMMENT '排序序号',
  PRIMARY KEY (`id`),
  KEY `recipe_id` (`recipe_id`),
  KEY `ingredient_id` (`ingredient_id`),
  CONSTRAINT `recipe_ingredients_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `recipe_ingredients_ibfk_2` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜谱食材子表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipe_ingredients`
--

LOCK TABLES `recipe_ingredients` WRITE;
/*!40000 ALTER TABLE `recipe_ingredients` DISABLE KEYS */;
INSERT INTO `recipe_ingredients` VALUES ('ri_0a490ff1eb','rec_cfe35aa5b9','ing_garlic_sprout',4.00,'根',0,1),('ri_0b03fe4b1c','rec_129c0cc024','ing_custom_132439a0',100.00,'适量',0,0),('ri_13b5bf7349','rec_129c0cc024','ing_ginger',0.00,'克',0,3),('ri_20d71716b0','rec_0d0a17ef8c','ing_light_soy',30.00,'毫升',0,4),('ri_23643ae6ce','rec_0d0a17ef8c','ing_pork_rib',500.00,'克',0,0),('ri_28e3e128ef','rec_5da0bd0274','ing_dried_chili',3.00,'个',0,1),('ri_2feeba3c72','rec_1b0b170448','ing_sugar',5.00,'克',0,4),('ri_3ae76ff9e5','rec_129c0cc024','ing_custom_475f2af8',3.00,'适量',0,2),('ri_3b80763575','rec_1b0b170448','ing_cooking_oil',15.00,'毫升',0,5),('ri_3f9a72faf3','rec_1b0b170448','ing_egg',3.00,'个',0,1),('ri_4beb1103b2','rec_129c0cc024','ing_light_soy',0.00,'毫升',0,5),('ri_50429666e0','rec_8281cf20c6','ing_bass',500.00,'克',0,1),('ri_5298624f4f','rec_0d0a17ef8c','ing_ginger',15.00,'克',0,1),('ri_55cfe416a2','rec_8281cf20c6','ing_cooking_oil',20.00,'毫升',0,5),('ri_57a8c7baab','rec_0d0a17ef8c','ing_rock_sugar',20.00,'克',0,6),('ri_5e6b2e786e','rec_1b0b170448','ing_custom_e1d5324b',0.00,'适量',0,6),('ri_6018a052f8','rec_1b0b170448','ing_custom_f5582e9c',0.00,'适量',0,8),('ri_6107942650','rec_6e440a1876','ing_egg',1.00,'个',0,1),('ri_61c57a2dfd','rec_1b0b170448','ing_salt',3.00,'克',0,3),('ri_7003668be0','rec_129c0cc024','ing_custom_8577f4b7',5.00,'适量',0,1),('ri_7d32ff062f','rec_0d0a17ef8c','ing_green_onion',10.00,'克',0,2),('ri_833319cc63','rec_5da0bd0274','ing_potato',2.00,'个',0,0),('ri_88f1798438','rec_0d0a17ef8c','ing_star_anise',2.00,'个',0,3),('ri_8940297571','rec_129c0cc024','ing_garlic',0.00,'瓣',0,4),('ri_8de37c97f1','rec_1b0b170448','ing_custom_60eadde0',0.00,'适量',0,7),('ri_9348baad8d','rec_1b0b170448','ing_green_onion',5.00,'克',0,2),('ri_9816b97978','rec_6e440a1876','ing_pork_tender',400.00,'克',0,0),('ri_a7a7d27132','rec_8281cf20c6','ing_light_soy',25.00,'毫升',0,4),('ri_b35af6b4e9','rec_0d0a17ef8c','ing_cooking_wine',20.00,'毫升',0,7),('ri_b8ccf0008f','rec_129c0cc024','ing_msg',0.00,'克',0,7),('ri_ba89d1129d','rec_1b0b170448','ing_tomato',300.00,'克',0,0),('ri_ccab9f3e12','rec_129c0cc024','ing_salt',0.00,'克',0,6),('ri_cf6c92aac5','rec_0d0a17ef8c','ing_dark_soy',10.00,'毫升',0,5),('ri_f511c8f6ac','rec_129c0cc024','ing_chicken_essence',0.00,'克',0,8),('ri_f8688c7d07','rec_8281cf20c6','ing_ginger',15.00,'克',0,3),('ri_fa041aec11','rec_cfe35aa5b9','ing_pork_belly',500.00,'克',0,0),('ri_ffedd54639','rec_8281cf20c6','ing_green_onion',20.00,'克',0,2);
/*!40000 ALTER TABLE `recipe_ingredients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipe_steps`
--

DROP TABLE IF EXISTS `recipe_steps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recipe_steps` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记录唯一标识',
  `recipe_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属菜谱ID',
  `step_number` int DEFAULT NULL COMMENT '步骤序号',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '步骤文字',
  `image` text COLLATE utf8mb4_unicode_ci COMMENT '步骤配图URL',
  PRIMARY KEY (`id`),
  KEY `recipe_id` (`recipe_id`),
  CONSTRAINT `recipe_steps_ibfk_1` FOREIGN KEY (`recipe_id`) REFERENCES `recipes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜谱步骤子表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipe_steps`
--

LOCK TABLES `recipe_steps` WRITE;
/*!40000 ALTER TABLE `recipe_steps` DISABLE KEYS */;
INSERT INTO `recipe_steps` VALUES ('rs_0372af5d45','rec_0d0a17ef8c',4,'加生抽、老抽翻炒均匀，倒入没过排骨的热水',NULL),('rs_040bb0b02a','rec_8281cf20c6',4,'倒掉盘中蒸出的腥水，淋上蒸鱼豉油',NULL),('rs_0b438a4c99','rec_0d0a17ef8c',1,'排骨洗净斩块，冷水下锅加料酒焯水，捞出冲洗干净',NULL),('rs_0bded0c3b8','rec_cfe35aa5b9',3,'锅中留底油，下豆瓣酱小火炒出红油',NULL),('rs_11446d0378','rec_1b0b170448',5,'撒上葱花出锅装盘',NULL),('rs_1518f9abb8','rec_6e440a1876',2,'裹蛋液淀粉，六成油温炸至金黄',NULL),('rs_182ae93567','rec_5da0bd0274',3,'下土豆丝大火快炒，加醋盐调味出锅',NULL),('rs_27460cae54','rec_0d0a17ef8c',5,'大火烧开转中小火炖30分钟，汤汁浓稠后大火收汁出锅',NULL),('rs_3d580a0316','rec_1b0b170448',2,'热锅凉油，倒入蛋液，快凝固时用筷子划散盛出',NULL),('rs_3e6f513fb4','rec_5da0bd0274',2,'热油爆香干辣椒和花椒',NULL),('rs_46b070a31e','rec_1b0b170448',3,'锅中再放少许油，下番茄块中火炒出汤汁',NULL),('rs_51510215fc','rec_1b0b170448',1,'番茄洗净切块，鸡蛋打散加少许盐和水淀粉搅匀',NULL),('rs_546b34ff0e','rec_cfe35aa5b9',4,'下姜片、大蒜爆香，倒回肉片翻炒均匀',NULL),('rs_663579709d','rec_8281cf20c6',1,'鲈鱼洗净，两面各划三刀，抹少许盐和料酒腌制10分钟',NULL),('rs_70d2fe3e2e','rec_8281cf20c6',2,'盘底铺姜片和葱段，放上鲈鱼',NULL),('rs_75bbb11154','rec_cfe35aa5b9',2,'锅中不放油，下肉片中火煸炒至出油卷曲呈灯盏窝状，盛出备用',NULL),('rs_79600bc208','rec_6e440a1876',1,'里脊肉切条，加盐料酒腌制15分钟',NULL),('rs_7ee2948f91','rec_cfe35aa5b9',1,'五花肉冷水下锅，加姜片料酒煮至筷子能扎透，捞出切薄片',NULL),('rs_7f173e6b27','rec_0d0a17ef8c',3,'下排骨快速翻炒上色，加姜片、葱段、八角炒香',NULL),('rs_83fe97ebd4','rec_0d0a17ef8c',2,'锅中放少许油，小火炒冰糖至枣红色冒泡',NULL),('rs_8b62250418','rec_cfe35aa5b9',5,'加生抽、少许陈醋和味精调味，大火翻炒出锅',NULL),('rs_b0d2c227ba','rec_8281cf20c6',3,'蒸锅水开后上锅大火蒸8-10分钟',NULL),('rs_b2c8dd2ca3','rec_5da0bd0274',1,'土豆切细丝，泡水去淀粉，沥干',NULL),('rs_ce6c2be3a2','rec_1b0b170448',4,'加白糖和少许盐调味，倒回鸡蛋翻炒均匀',NULL),('rs_e124ed06f6','rec_6e440a1876',3,'糖醋汁勾芡，下肉条快速翻匀出锅',NULL),('rs_e643cddb96','rec_8281cf20c6',5,'铺上葱丝姜丝，浇上滚烫热油激出香味即可',NULL);
/*!40000 ALTER TABLE `recipe_steps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recipes`
--

DROP TABLE IF EXISTS `recipes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recipes` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜谱唯一标识',
  `name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜品名称',
  `image` text COLLATE utf8mb4_unicode_ci COMMENT '菜品图片URL',
  `emoji` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT 0xF09F8DB3 COMMENT '菜品emoji',
  `tenant_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属家庭（null=个人私有）',
  `owner_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '创建者userId',
  `status` enum('mastered','learning') COLLATE utf8mb4_unicode_ci DEFAULT 'mastered' COMMENT '拿手菜/待学菜谱',
  `category` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '分类：肉类/蔬菜/海鲜/素面食/汤类/饮品/甜品',
  `difficulty` varchar(8) COLLATE utf8mb4_unicode_ci DEFAULT '3',
  `cook_time` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '制作耗时',
  `flavor_tags` json DEFAULT NULL COMMENT '口味标签数组：咸鲜/麻辣/酸甜/清淡/酱香等',
  `meat_type` enum('meat','veg','mix') COLLATE utf8mb4_unicode_ci DEFAULT 'mix' COMMENT '荤/素/荤素搭配',
  `servings` int DEFAULT '4' COMMENT '当前设定的用餐人数',
  `cook_count` int DEFAULT '0',
  `staple_weight` decimal(8,2) DEFAULT NULL COMMENT '主食重量（克），null=未设定',
  `is_favorited` tinyint(1) DEFAULT '0' COMMENT '是否收藏',
  `is_shared` tinyint(1) DEFAULT '0' COMMENT '是否共享到家庭',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT '备注/小贴士',
  `source` text COLLATE utf8mb4_unicode_ci COMMENT '待学来源链接',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `recipes_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE SET NULL,
  CONSTRAINT `recipes_ibfk_2` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜谱表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recipes`
--

LOCK TABLES `recipes` WRITE;
/*!40000 ALTER TABLE `recipes` DISABLE KEYS */;
INSERT INTO `recipes` VALUES ('rec_0d0a17ef8c','红烧排骨','https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','3','40分钟','[\"咸鲜\", \"酱香\"]','meat',4,17,NULL,0,0,'','','2026-06-16 14:40:05','2026-06-18 15:00:07'),('rec_129c0cc024','麻婆豆腐','/uploads/f631c7570005474bb355cfba4a9ad2d1.png','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','3','20分钟','[\"麻辣\"]','meat',3,15,NULL,0,0,'','','2026-06-16 17:00:03','2026-06-18 14:58:11'),('rec_1920f5eb01','地三鲜','https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','素菜','2','20分钟','[\"咸鲜\", \"酱香\"]','veg',4,0,NULL,0,0,'土豆茄子辣椒都要过油才香','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_1b0b170448','番茄炒蛋','https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','素菜','1','10分钟','[\"咸鲜\"]','mix',3,11,NULL,0,0,'','','2026-06-16 14:40:06','2026-06-18 14:58:11'),('rec_30f591ef88','蒜蓉西兰花','https://images.unsplash.com/photo-1547592166-23ac45744acd?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','素菜','1','10分钟','[\"蒜香\", \"清淡\"]','veg',3,0,NULL,0,0,'焯水时加盐和油保持翠绿','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_3817349f4e','紫菜蛋花汤','https://images.unsplash.com/photo-1547592166-23ac45744acd?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','汤类','1','5分钟','[\"清淡\"]','mix',3,33,NULL,0,0,'','','2026-06-16 18:15:52','2026-06-18 14:58:11'),('rec_574e57d6b8','冰镇酸梅汤','https://images.unsplash.com/photo-1547592166-23ac45744acd?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','饮品','1','30分钟','[\"酸甜\", \"清凉\"]','veg',6,0,NULL,0,0,'乌梅、山楂、甘草、冰糖同煮','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_5da0bd0274','酸辣土豆丝','/uploads/1fb4cd197d374da5ae636f39090cb965.png','🍳',NULL,'wx_bzlqzuagcb','mastered','素菜','1','10分钟','[\"酸辣\"]','veg',3,52,NULL,0,0,'','','2026-06-16 18:15:52','2026-06-18 14:58:11'),('rec_6e440a1876','糖醋里脊','https://images.unsplash.com/photo-1525755662778-989d0524087e?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','3','25分钟','[\"酸甜\"]','meat',4,22,NULL,0,0,'','','2026-06-16 18:15:52','2026-06-18 14:58:11'),('rec_703d411626','冬瓜排骨汤','https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','汤类','2','60分钟','[\"咸鲜\", \"清淡\"]','meat',6,0,NULL,0,0,'排骨先焯水去血沫','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_7058b10f90','鱼香肉丝','https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','3','25分钟','[\"酸甜\", \"微辣\"]','meat',4,0,NULL,0,0,'鱼香汁比例：醋2糖2生抽1','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_8281cf20c6','清蒸鲈鱼','https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','2','20分钟','[\"咸鲜\", \"清淡\"]','meat',4,27,NULL,0,0,'','','2026-06-16 14:40:06','2026-06-18 14:58:11'),('rec_917097f6de','沱牌特曲','/uploads/b52d5a8e9aef495dbceef045031cdd78.png','🍳',NULL,'wx_bzlqzuagcb','mastered','饮品','3','','[]','mix',4,0,NULL,0,0,'','','2026-06-18 18:12:39','2026-06-18 18:12:57'),('rec_92af4b56cd','1','/uploads/8a899a1704b8486793638d94c1d53e5a.png','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','3','','[]','mix',4,0,NULL,0,0,'','','2026-06-18 15:39:47','2026-06-18 18:01:22'),('rec_a6a4b3f95c','煎饺','https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','小吃','2','20分钟','[\"酥脆\", \"咸鲜\"]','meat',4,0,NULL,0,0,'先煎底再加水焖，底脆馅嫩','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_bc0e38d2f6','酸辣汤','https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','汤类','2','15分钟','[\"酸辣\", \"开胃\"]','mix',4,0,NULL,0,0,'醋最后放，保持酸味','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_c431b92f55','蒜泥白肉','https://images.unsplash.com/photo-1559847844-5315695dadae?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','凉菜','2','30分钟','[\"蒜香\", \"咸鲜\"]','meat',4,0,NULL,0,0,'五花肉煮到筷子能轻松插入','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_c5d6f82074','凉拌木耳','https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','凉菜','1','10分钟','[\"酸辣\", \"清爽\"]','veg',3,0,NULL,0,0,'木耳提前泡发2小时','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_cd33709f85','宫保鸡丁','https://images.unsplash.com/photo-1525755662778-989d0524087e?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','2','20分钟','[\"麻辣\", \"咸鲜\"]','meat',4,0,NULL,0,0,'花生米最后放，保持酥脆','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_cfe35aa5b9','回锅肉','/uploads/f91cb00455e040768a21ff6d9ca467a9.png','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','3','30分钟','[\"咸鲜\", \"酱香\"]','meat',4,29,NULL,0,0,'','','2026-06-16 15:54:18','2026-06-18 14:58:11'),('rec_d9bf5eb5ff','自制豆浆','https://images.unsplash.com/photo-1544025162-d76694265947?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','饮品','1','20分钟','[\"香浓\"]','veg',4,0,NULL,0,0,'黄豆提前泡一夜，打浆后煮沸','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_dbdc9b452c','水煮鱼','https://images.unsplash.com/photo-1559847844-5315695dadae?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','4','30分钟','[\"麻辣\", \"咸鲜\"]','meat',4,18,NULL,0,0,'','','2026-06-16 18:15:52','2026-06-18 14:58:11'),('rec_e4af55084d','春卷','https://images.unsplash.com/photo-1559847844-5315695dadae?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','小吃','2','30分钟','[\"酥脆\", \"咸鲜\"]','mix',6,0,NULL,0,0,'油温七成热下锅，金黄捞出','','2026-06-18 17:58:24','2026-06-18 17:58:24'),('rec_f7408488fc','干煸四季豆','https://images.unsplash.com/photo-1582452919408-aca2a2c9d67b?w=600&h=600&fit=crop','🍳',NULL,'wx_bzlqzuagcb','mastered','热菜','2','15分钟','[\"咸鲜\", \"微辣\"]','veg',3,0,NULL,0,0,'豆角一定要煸到起皱才香','','2026-06-18 17:58:24','2026-06-18 17:58:24');
/*!40000 ALTER TABLE `recipes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenant_members`
--

DROP TABLE IF EXISTS `tenant_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenant_members` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '记录唯一标识',
  `tenant_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '家庭ID',
  `user_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '成员userId',
  `role` enum('owner','member') COLLATE utf8mb4_unicode_ci DEFAULT 'member' COMMENT '角色',
  `joined_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `tenant_members_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenants` (`id`) ON DELETE CASCADE,
  CONSTRAINT `tenant_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='家庭成员表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenant_members`
--

LOCK TABLES `tenant_members` WRITE;
/*!40000 ALTER TABLE `tenant_members` DISABLE KEYS */;
INSERT INTO `tenant_members` VALUES ('tm_bd833ae11f','t_deff3ec1','wx_bzlqzuagcb','owner','2026-06-16 21:43:07');
/*!40000 ALTER TABLE `tenant_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenants`
--

DROP TABLE IF EXISTS `tenants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenants` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '家庭唯一标识',
  `name` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '家庭名称',
  `owner_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '户主userId',
  `invite_code` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '邀请码/二维码标识',
  `member_count` int DEFAULT '1' COMMENT '成员数',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  PRIMARY KEY (`id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `tenants_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='家庭表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenants`
--

LOCK TABLES `tenants` WRITE;
/*!40000 ALTER TABLE `tenants` DISABLE KEYS */;
INSERT INTO `tenants` VALUES ('t_deff3ec1','风矢云散的家','wx_bzlqzuagcb','AT3224AB',1,'2026-06-16 21:43:07','2026-06-16 21:43:07'),('test_tenant','测试家庭',NULL,'TEST001',1,'2026-06-12 18:24:45','2026-06-12 18:24:45');
/*!40000 ALTER TABLE `tenants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户唯一标识，微信OpenID',
  `nickname` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '微信昵称',
  `avatar` text COLLATE utf8mb4_unicode_ci COMMENT '微信头像URL',
  `default_servings` int DEFAULT '4' COMMENT '默认用餐人数',
  `unit_preference` enum('g','jin') COLLATE utf8mb4_unicode_ci DEFAULT 'g' COMMENT '计量单位：克/斤',
  `preferences` json DEFAULT NULL,
  `memory_enabled` tinyint(1) DEFAULT '1' COMMENT '配比记忆开关',
  `home_tenant_id` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '当前加入的家庭ID',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('guest_1781252210360','游客',NULL,4,'g','{\"caipu_spice\": [{\"id\": \"ing_sichuan_pepper\", \"name\": \"花椒\", \"unit\": \"克\", \"emoji\": \"🌶️\"}, {\"id\": \"ing_star_anise\", \"name\": \"八角\", \"unit\": \"个\", \"emoji\": \"⭐\"}, {\"id\": \"ing_cinnamon\", \"name\": \"桂皮\", \"unit\": \"小块\", \"emoji\": \"🪵\"}, {\"id\": \"ing_bay_leaf\", \"name\": \"香叶\", \"unit\": \"片\", \"emoji\": \"🌿\"}, {\"id\": \"ing_dried_chili\", \"name\": \"干辣椒\", \"unit\": \"个\", \"emoji\": \"🌶️\"}, {\"id\": \"ing_cumin\", \"name\": \"孜然\", \"unit\": \"克\", \"emoji\": \"🌿\"}, {\"id\": \"ing_fennel\", \"name\": \"小茴香\", \"unit\": \"克\", \"emoji\": \"🌿\"}, {\"id\": \"ing_sesame\", \"name\": \"芝麻\", \"unit\": \"克\", \"emoji\": \"🫘\"}, {\"id\": \"ing_ginger\", \"name\": \"生姜\", \"unit\": \"克\", \"emoji\": \"🫚\"}, {\"id\": \"ing_garlic\", \"name\": \"大蒜\", \"unit\": \"瓣\", \"emoji\": \"🧄\"}, {\"id\": \"ing_green_onion\", \"name\": \"小葱\", \"unit\": \"根\", \"emoji\": \"🌱\"}, {\"id\": \"ing_cilantro\", \"name\": \"香菜\", \"unit\": \"根\", \"emoji\": \"🌿\"}, {\"id\": \"ing_chili_sauce\", \"name\": \"辣椒酱\", \"unit\": \"克\", \"emoji\": \"🌶️\"}, {\"id\": \"ing_chili_oil\", \"name\": \"辣椒油\", \"unit\": \"毫升\", \"emoji\": \"🌶️\"}], \"caipu_seasoning\": [{\"id\": \"ing_salt\", \"name\": \"食盐\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_sugar\", \"name\": \"白砂糖\", \"unit\": \"克\", \"emoji\": \"🍬\"}, {\"id\": \"ing_msg\", \"name\": \"味精\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_chicken_essence\", \"name\": \"鸡精\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_light_soy\", \"name\": \"生抽\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_dark_soy\", \"name\": \"老抽\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_oyster_sauce\", \"name\": \"蚝油\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_vinegar\", \"name\": \"陈醋\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_fragrant_vinegar\", \"name\": \"香醋\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_cooking_wine\", \"name\": \"料酒\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_bean_paste\", \"name\": \"豆瓣酱\", \"unit\": \"克\", \"emoji\": \"🫗\"}, {\"id\": \"ing_rock_sugar\", \"name\": \"冰糖\", \"unit\": \"克\", \"emoji\": \"🍬\"}, {\"id\": \"ing_sesame_oil\", \"name\": \"香油\", \"unit\": \"毫升\", \"emoji\": \"🫒\"}, {\"id\": \"ing_cooking_oil\", \"name\": \"食用油\", \"unit\": \"毫升\", \"emoji\": \"🫒\"}, {\"id\": \"ing_white_pepper\", \"name\": \"白胡椒粉\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_black_pepper\", \"name\": \"黑胡椒粉\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_sichuan_pepper_powder\", \"name\": \"花椒面\", \"unit\": \"克\", \"emoji\": \"🧂\"}]}',1,NULL,'2026-06-18 14:03:13','2026-06-18 14:38:03'),('test_user','家庭大厨',NULL,4,'g','{\"caipu_market_favs\": [{\"id\": \"ing_pork_belly\", \"name\": \"五花肉\", \"emoji\": \"🥩\"}, \"ing_custom_00bc74aa\", \"ing_yam\", \"ing_ginger\", \"ing_pork_belly\", \"ing_pork_rib\", \"ing_beef_omasum\"], \"caipu_monthly_budget\": 3000}',1,NULL,'2026-06-17 13:16:27','2026-06-17 13:16:29'),('wx_86ysmdm65s','家庭大厨',NULL,4,'g',NULL,1,NULL,'2026-06-17 13:06:41','2026-06-17 13:06:41'),('wx_bzlqzuagcb',NULL,NULL,3,'g','{\"caipu_spice\": [{\"id\": \"ing_sichuan_pepper\", \"name\": \"花椒\", \"unit\": \"克\", \"emoji\": \"🌶️\"}, {\"id\": \"ing_star_anise\", \"name\": \"八角\", \"unit\": \"个\", \"emoji\": \"⭐\"}, {\"id\": \"ing_cinnamon\", \"name\": \"桂皮\", \"unit\": \"小块\", \"emoji\": \"🪵\"}, {\"id\": \"ing_bay_leaf\", \"name\": \"香叶\", \"unit\": \"片\", \"emoji\": \"🌿\"}, {\"id\": \"ing_dried_chili\", \"name\": \"干辣椒\", \"unit\": \"个\", \"emoji\": \"🌶️\"}, {\"id\": \"ing_cumin\", \"name\": \"孜然\", \"unit\": \"克\", \"emoji\": \"🌿\"}, {\"id\": \"ing_fennel\", \"name\": \"小茴香\", \"unit\": \"克\", \"emoji\": \"🌿\"}, {\"id\": \"ing_sesame\", \"name\": \"芝麻\", \"unit\": \"克\", \"emoji\": \"🫘\"}, {\"id\": \"ing_ginger\", \"name\": \"生姜\", \"unit\": \"克\", \"emoji\": \"🫚\"}, {\"id\": \"ing_garlic\", \"name\": \"大蒜\", \"unit\": \"瓣\", \"emoji\": \"🧄\"}, {\"id\": \"ing_green_onion\", \"name\": \"小葱\", \"unit\": \"根\", \"emoji\": \"🌱\"}, {\"id\": \"ing_cilantro\", \"name\": \"香菜\", \"unit\": \"根\", \"emoji\": \"🌿\"}, {\"id\": \"ing_chili_sauce\", \"name\": \"辣椒酱\", \"unit\": \"克\", \"emoji\": \"🌶️\"}, {\"id\": \"ing_chili_oil\", \"name\": \"辣椒油\", \"unit\": \"毫升\", \"emoji\": \"🌶️\"}], \"caipu_dev_uid\": \"wx_bzlqzuagcb\", \"caipu_seasoning\": [{\"id\": \"ing_salt\", \"name\": \"食盐\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_sugar\", \"name\": \"白砂糖\", \"unit\": \"克\", \"emoji\": \"🍬\"}, {\"id\": \"ing_msg\", \"name\": \"味精\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_chicken_essence\", \"name\": \"鸡精\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_light_soy\", \"name\": \"生抽\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_dark_soy\", \"name\": \"老抽\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_oyster_sauce\", \"name\": \"蚝油\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_vinegar\", \"name\": \"陈醋\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_fragrant_vinegar\", \"name\": \"香醋\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_cooking_wine\", \"name\": \"料酒\", \"unit\": \"毫升\", \"emoji\": \"🫗\"}, {\"id\": \"ing_bean_paste\", \"name\": \"豆瓣酱\", \"unit\": \"克\", \"emoji\": \"🫗\"}, {\"id\": \"ing_rock_sugar\", \"name\": \"冰糖\", \"unit\": \"克\", \"emoji\": \"🍬\"}, {\"id\": \"ing_sesame_oil\", \"name\": \"香油\", \"unit\": \"毫升\", \"emoji\": \"🫒\"}, {\"id\": \"ing_cooking_oil\", \"name\": \"食用油\", \"unit\": \"毫升\", \"emoji\": \"🫒\"}, {\"id\": \"ing_white_pepper\", \"name\": \"白胡椒粉\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_black_pepper\", \"name\": \"黑胡椒粉\", \"unit\": \"克\", \"emoji\": \"🧂\"}, {\"id\": \"ing_sichuan_pepper_powder\", \"name\": \"花椒面\", \"unit\": \"克\", \"emoji\": \"🧂\"}], \"caipu_categories\": [{\"name\": \"热菜\", \"emoji\": \"🍳\"}, {\"name\": \"凉菜\", \"emoji\": \"🥗\"}, {\"name\": \"素菜\", \"emoji\": \"🥬\"}, {\"name\": \"小吃\", \"emoji\": \"🥟\"}, {\"name\": \"汤类\", \"emoji\": \"🥣\"}, {\"name\": \"酒饮\", \"emoji\": \"🥃\"}, {\"name\": \"白酒\", \"emoji\": \"🍶\"}, {\"name\": \"1\", \"emoji\": \"🌮\"}], \"caipu_default_loc\": \"南坛菜市场\", \"caipu_feast_title\": \"端午节\", \"caipu_hidden_cats\": [\"0\", \"1\", \"2\", \"3\", \"4\", \"5\", \"6\", \"酒饮\", \"11\"], \"caipu_market_favs\": [{\"id\": \"ing_pork_belly\", \"name\": \"五花肉\", \"emoji\": \"🥩\"}, \"ing_custom_00bc74aa\", \"ing_yam\", \"ing_ginger\", \"ing_pork_belly\", \"ing_pork_rib\", \"ing_beef_omasum\", \"ing_pear\", \"ing_cherry\", \"ing_tangerine\", \"ing_orange\"], \"caipu_market_locs\": [\"南坛菜市场\", \"菜市场\", \"超市\", \"线上\"], \"caipu_feast_dishes\": {\"凉菜\": [{\"id\": \"rec_c431b92f55\", \"name\": \"蒜泥白肉\", \"emoji\": \"🍳\"}, {\"id\": \"rec_c5d6f82074\", \"name\": \"凉拌木耳\", \"emoji\": \"🍳\"}], \"小吃\": [{\"id\": \"rec_a6a4b3f95c\", \"name\": \"煎饺\", \"emoji\": \"🍳\"}, {\"id\": \"rec_e4af55084d\", \"name\": \"春卷\", \"emoji\": \"🍳\"}], \"汤类\": [{\"id\": \"rec_703d411626\", \"name\": \"冬瓜排骨汤\", \"emoji\": \"🍳\"}, {\"id\": \"rec_bc0e38d2f6\", \"name\": \"酸辣汤\", \"emoji\": \"🍳\"}], \"热菜\": [{\"id\": \"rec_0d0a17ef8c\", \"name\": \"红烧排骨\", \"emoji\": \"🍳\"}, {\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}, {\"id\": \"rec_6e440a1876\", \"name\": \"糖醋里脊\", \"emoji\": \"🍳\"}, {\"id\": \"rec_cfe35aa5b9\", \"name\": \"回锅肉\", \"emoji\": \"🍳\"}, {\"id\": \"rec_dbdc9b452c\", \"name\": \"水煮鱼\", \"emoji\": \"🍳\"}], \"白酒\": [], \"素菜\": [{\"id\": \"rec_1b0b170448\", \"name\": \"番茄炒蛋\", \"emoji\": \"🍳\"}, {\"id\": \"rec_5da0bd0274\", \"name\": \"酸辣土豆丝\", \"emoji\": \"🍳\"}, {\"id\": \"rec_1920f5eb01\", \"name\": \"地三鲜\", \"emoji\": \"🍳\"}, {\"id\": \"rec_30f591ef88\", \"name\": \"蒜蓉西兰花\", \"emoji\": \"🍳\"}]}, \"caipu_feast_footer\": \"家庭私厨  ·  家的味道\", \"caipu_feast_records\": [{\"id\": 1781772966625, \"date\": \"2026-06-18\", \"title\": \"国庆宴\", \"dishes\": {\"凉菜\": [], \"小吃\": [], \"汤菜\": [{\"id\": \"rec_3817349f4e\", \"name\": \"紫菜蛋花汤\", \"emoji\": \"🍳\"}], \"热菜\": [{\"id\": \"rec_0d0a17ef8c\", \"name\": \"红烧排骨\", \"emoji\": \"🍳\"}, {\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}, {\"id\": \"rec_6e440a1876\", \"name\": \"糖醋里脊\", \"emoji\": \"🍳\"}, {\"id\": \"rec_8281cf20c6\", \"name\": \"清蒸鲈鱼\", \"emoji\": \"🍳\"}, {\"id\": \"rec_cfe35aa5b9\", \"name\": \"回锅肉\", \"emoji\": \"🍳\"}, {\"id\": \"rec_dbdc9b452c\", \"name\": \"水煮鱼\", \"emoji\": \"🍳\"}], \"素菜\": [{\"id\": \"rec_1b0b170448\", \"name\": \"番茄炒蛋\", \"emoji\": \"🍳\"}, {\"id\": \"rec_5da0bd0274\", \"name\": \"酸辣土豆丝\", \"emoji\": \"🍳\"}]}, \"template\": 1}, {\"id\": 1781768233793, \"date\": \"2026-06-18\", \"title\": \"国庆宴\", \"dishes\": {\"凉菜\": [{\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}], \"小吃\": [], \"汤菜\": [], \"热菜\": [{\"id\": \"rec_0d0a17ef8c\", \"name\": \"红烧排骨\", \"emoji\": \"🍳\"}, {\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}, {\"id\": \"rec_6e440a1876\", \"name\": \"糖醋里脊\", \"emoji\": \"🍳\"}, {\"id\": \"rec_8281cf20c6\", \"name\": \"清蒸鲈鱼\", \"emoji\": \"🍳\"}, {\"id\": \"rec_cfe35aa5b9\", \"name\": \"回锅肉\", \"emoji\": \"🍳\"}, {\"id\": \"rec_dbdc9b452c\", \"name\": \"水煮鱼\", \"emoji\": \"🍳\"}]}, \"template\": 1}, {\"id\": 1781768221784, \"date\": \"2026-06-18\", \"title\": \"国庆宴\", \"dishes\": {\"凉菜\": [{\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}, {\"id\": \"rec_0d0a17ef8c\", \"name\": \"红烧排骨\", \"emoji\": \"🍳\"}], \"小吃\": [], \"汤菜\": [], \"热菜\": [{\"id\": \"rec_0d0a17ef8c\", \"name\": \"红烧排骨\", \"emoji\": \"🍳\"}, {\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}, {\"id\": \"rec_6e440a1876\", \"name\": \"糖醋里脊\", \"emoji\": \"🍳\"}, {\"id\": \"rec_8281cf20c6\", \"name\": \"清蒸鲈鱼\", \"emoji\": \"🍳\"}, {\"id\": \"rec_cfe35aa5b9\", \"name\": \"回锅肉\", \"emoji\": \"🍳\"}, {\"id\": \"rec_dbdc9b452c\", \"name\": \"水煮鱼\", \"emoji\": \"🍳\"}]}, \"template\": 1}, {\"id\": 1781767821581, \"date\": \"2026-06-18\", \"title\": \"我的家宴\", \"dishes\": {\"凉菜\": [{\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}, {\"id\": \"rec_0d0a17ef8c\", \"name\": \"红烧排骨\", \"emoji\": \"🍳\"}], \"小吃\": [], \"汤菜\": [], \"热菜\": [{\"id\": \"rec_0d0a17ef8c\", \"name\": \"红烧排骨\", \"emoji\": \"🍳\"}, {\"id\": \"rec_129c0cc024\", \"name\": \"麻婆豆腐\", \"emoji\": \"🍳\"}, {\"id\": \"rec_6e440a1876\", \"name\": \"糖醋里脊\", \"emoji\": \"🍳\"}, {\"id\": \"rec_8281cf20c6\", \"name\": \"清蒸鲈鱼\", \"emoji\": \"🍳\"}, {\"id\": \"rec_cfe35aa5b9\", \"name\": \"回锅肉\", \"emoji\": \"🍳\"}, {\"id\": \"rec_dbdc9b452c\", \"name\": \"水煮鱼\", \"emoji\": \"🍳\"}]}, \"template\": 1}], \"caipu_feast_showDate\": 1, \"caipu_feast_template\": 1, \"caipu_market_loc_pos\": {\"南坛菜市场\": \"50% 50%\"}, \"caipu_monthly_budget\": 4000, \"caipu_feast_showTitle\": 1, \"caipu_market_loc_imgs\": {\"南坛菜市场\": \"/uploads/12d5081076cd4ff7bfefd8eb73da88cc.png\"}, \"caipu_feast_banner_img\": \"/uploads/af396a748be345a3b1eb046b5fadf526.png\", \"caipu_feast_banner_pos\": \"90% 70%\", \"caipu_feast_showFooter\": 1, \"caipu_meals_banner_img\": \"/uploads/5fa7fea3e17b4cee8f0e9db8bfb2c6da.png\", \"caipu_meals_banner_pos\": \"75% 45%\", \"caipu_feast_banner_blur\": 20, \"caipu_profile_banner_img\": \"/uploads/1b1775c6a523496990cbd641b06fe6bd.png\", \"caipu_profile_banner_pos\": \"50% 40%\"}',1,'t_deff3ec1','2026-06-16 14:33:31','2026-06-18 18:24:13');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-18 18:26:30
