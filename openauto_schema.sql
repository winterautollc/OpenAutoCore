/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `vehicle_id` int unsigned DEFAULT NULL,
  `vin` varchar(30) DEFAULT NULL,
  `appointment_date` date NOT NULL,
  `appointment_time` time NOT NULL,
  `notes` text,
  `status` enum('scheduled','completed','missed','cancelled','rescheduled') DEFAULT 'scheduled',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `dropoff_type` enum('drop','wait') DEFAULT 'drop',
  `last_updated` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `fk_appointments_vehicle` (`vehicle_id`),
  CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_appointments_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `last_name` varchar(30) DEFAULT NULL,
  `first_name` varchar(30) NOT NULL,
  `address` varchar(100) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `zip` varchar(15) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `alt_phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `archived` tinyint(1) DEFAULT (0),
  PRIMARY KEY (`customer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estimate_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `estimate_id` int NOT NULL,
  `ro_id` int DEFAULT NULL,
  `item_description` varchar(255) NOT NULL,
  `qty` decimal(10,2) NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `total_price` decimal(10,2) NOT NULL,
  `type` varchar(15) DEFAULT NULL,
  `archived` tinyint(1) DEFAULT (0),
  `part_number` varchar(64) DEFAULT NULL,
  `unit_cost` decimal(10,2) NOT NULL DEFAULT '0.00',
  `taxable` tinyint(1) NOT NULL DEFAULT '1',
  `vendor` varchar(100) DEFAULT NULL,
  `source` varchar(32) NOT NULL DEFAULT 'manual',
  `metadata` json DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `estimate_id` (`estimate_id`),
  CONSTRAINT `estimate_items_ibfk_1` FOREIGN KEY (`estimate_id`) REFERENCES `estimates` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `estimates` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `estimate_date` date NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `technician` varchar(100) DEFAULT NULL,
  `writer` varchar(100) DEFAULT NULL,
  `archived` tinyint(1) DEFAULT (0),
  `assigned_writer_id` int DEFAULT NULL,
  `assigned_tech_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `idx_est_writer` (`assigned_writer_id`),
  KEY `idx_est_tech` (`assigned_tech_id`),
  KEY `idx_est_archived` (`archived`),
  CONSTRAINT `estimates_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_est_tech` FOREIGN KEY (`assigned_tech_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_est_writer` FOREIGN KEY (`assigned_writer_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `estimate_id` int NOT NULL,
  `invoice_date` date NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `payment_status` enum('Unpaid','Paid','Overdue') DEFAULT 'Unpaid',
  `archived` tinyint(1) DEFAULT (0),
  PRIMARY KEY (`id`),
  KEY `estimate_id` (`estimate_id`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`estimate_id`) REFERENCES `estimates` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `labor_rates` (
  `labor_rate` float(10,2) DEFAULT NULL,
  `labor_type` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pricing_matrix` (
  `id` int NOT NULL AUTO_INCREMENT,
  `min_cost` decimal(10,2) DEFAULT NULL,
  `max_cost` decimal(10,2) DEFAULT NULL,
  `multiplier` decimal(10,4) DEFAULT NULL,
  `percent_return` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repair_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `appointment_id` int DEFAULT NULL,
  `customer_id` int NOT NULL,
  `vehicle_id` int unsigned NOT NULL,
  `status` enum('open','approved','working','checkout','archived') NOT NULL DEFAULT 'open',
  `ro_number` varchar(10) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `locked_by` varchar(255) DEFAULT NULL,
  `locked_at` timestamp NULL DEFAULT NULL,
  `miles_in` int DEFAULT NULL,
  `miles_out` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `assigned_writer_id` int DEFAULT NULL,
  `assigned_tech_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ro_number` (`ro_number`),
  KEY `customer_id` (`customer_id`),
  KEY `appointment_id` (`appointment_id`),
  KEY `fk_ro_vehicle` (`vehicle_id`),
  KEY `idx_ro_created_by` (`created_by`),
  KEY `fk_ro_writer` (`assigned_writer_id`),
  KEY `fk_ro_tech` (`assigned_tech_id`),
  CONSTRAINT `fk_ro_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_ro_tech` FOREIGN KEY (`assigned_tech_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_ro_vehicle` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_ro_writer` FOREIGN KEY (`assigned_writer_id`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `repair_orders_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `repair_orders_ibfk_3` FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ro_c3_lines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ro_id` int NOT NULL,
  `line_no` int NOT NULL DEFAULT '1',
  `concern` text NOT NULL,
  `cause` text,
  `correction` text,
  `estimate_item_id` int DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_c3_author` (`created_by`),
  KEY `ro_id` (`ro_id`,`line_no`),
  KEY `estimate_item_id` (`estimate_item_id`),
  CONSTRAINT `fk_c3_author` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_c3_item` FOREIGN KEY (`estimate_item_id`) REFERENCES `estimate_items` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_c3_ro` FOREIGN KEY (`ro_id`) REFERENCES `repair_orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `shop_info` (
  `shop_name` varchar(255) DEFAULT NULL,
  `facility_id` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `zip` varchar(255) DEFAULT NULL,
  `disclaimer` mediumtext,
  `warranty_duration` tinyint DEFAULT NULL,
  `warranty_time` tinyint DEFAULT NULL,
  `months` varchar(255) DEFAULT NULL,
  `miles` varchar(255) DEFAULT NULL,
  `shop_logo` mediumblob,
  `id` int NOT NULL AUTO_INCREMENT,
  `sales_tax_rate` decimal(4,2) DEFAULT NULL,
  `labor_rate` decimal(3,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_sessions` (
  `token` char(64) NOT NULL,
  `user_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`token`),
  KEY `fk_user_sessions_user` (`user_id`),
  CONSTRAINT `fk_user_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_settings` (
  `user_id` int NOT NULL,
  `theme` varchar(32) NOT NULL DEFAULT 'light',
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_user_settings_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `user_settings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `chk_theme_valid` CHECK ((`theme` in (_utf8mb4'light',_utf8mb4'dark',_utf8mb4'system'))),
  CONSTRAINT `user_settings_chk_1` CHECK ((`theme` in (_utf8mb4'light',_utf8mb4'dark',_utf8mb4'system')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `user_type` enum('writer','technician','manager') NOT NULL DEFAULT 'writer',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `phone` varchar(15) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vehicles` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `vin` varchar(17) DEFAULT NULL,
  `year` varchar(30) DEFAULT NULL,
  `make` varchar(30) DEFAULT NULL,
  `model` varchar(30) DEFAULT NULL,
  `engine_size` varchar(30) DEFAULT NULL,
  `trim` varchar(50) DEFAULT NULL,
  `customer_id` int DEFAULT NULL,
  `archived` tinyint(1) DEFAULT (0),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_vehicles_vin` (`vin`),
  KEY `idx_vehicles_customer` (`customer_id`),
  CONSTRAINT `fk_vehicles_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

