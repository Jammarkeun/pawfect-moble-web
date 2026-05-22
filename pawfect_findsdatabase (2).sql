SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

CREATE DATABASE IF NOT EXISTS `pawfect_finds_database` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `pawfect_finds_database`;

CREATE TABLE `cache_entries` (
  `cache_key` varchar(255) NOT NULL,
  `cache_value` longtext NOT NULL,
  `expires_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `cart` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `added_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `variant_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `name`, `description`, `image_url`, `is_active`, `created_at`) VALUES
(1, 'Dog Food & Treats', 'Premium dog food, treats, and nutritional supplements for all dog breeds and ages', NULL, 1, '2025-10-22 10:56:35'),
(2, 'Cat Litter & Accessories', 'Cat litter, litter boxes, toys, scratching posts, and feline accessories', NULL, 1, '2025-10-22 10:56:35'),
(3, 'Aquariums & Fish Supplies', 'Fish tanks, filters, pumps, decorations, and aquarium maintenance supplies', NULL, 1, '2025-10-22 10:56:35'),
(4, 'Bird Feeders & Food', 'Bird cages, feeders, perches, toys, and specialized bird food', NULL, 1, '2025-10-22 10:56:35'),
(5, 'Pet Grooming Products', 'Shampoos, brushes, nail clippers, grooming tools, and spa products', NULL, 1, '2025-10-22 10:56:35'),
(6, 'Pet Health & Wellness', 'Vitamins, supplements, first aid supplies, and health monitoring products', NULL, 1, '2025-10-22 10:56:35');

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages`
--

CREATE TABLE `chat_messages` (
  `id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `sender_role` enum('customer','seller','admin','rider') DEFAULT NULL,
  `message` text NOT NULL,
  `is_support` tinyint(1) NOT NULL DEFAULT 0,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `chat_messages`
--

INSERT INTO `chat_messages` (`id`, `room_id`, `user_id`, `sender_role`, `message`, `is_support`, `is_read`, `created_at`) VALUES
(1, 1, 16, 'customer', 'help me in my registration', 0, 1, '2025-11-04 04:32:52'),
(2, 1, 16, 'customer', 'help', 0, 1, '2025-11-04 04:44:12'),
(3, 2, 1, 'admin', 'hey', 1, 0, '2025-11-04 04:48:25'),
(4, 2, 1, 'admin', 'hey', 1, 0, '2025-11-04 04:51:49'),
(5, 2, 1, 'admin', 'hey', 1, 0, '2025-11-04 04:56:51'),
(6, 1, 16, 'customer', 'yow', 0, 1, '2025-11-04 04:59:47'),
(7, 1, 16, 'customer', 'hays', 0, 1, '2025-11-04 05:04:53'),
(8, 1, 16, 'customer', 'miss u', 0, 1, '2025-11-04 05:04:56'),
(9, 2, 1, 'admin', 'hey', 1, 0, '2025-11-04 05:06:38'),
(10, 1, 16, 'customer', 'miss u', 0, 1, '2025-11-04 05:08:05'),
(11, 2, 1, 'admin', 'hey bro', 1, 0, '2025-11-04 05:12:27'),
(12, 2, 1, 'admin', 'ayo', 1, 0, '2025-11-04 05:17:23'),
(13, 1, 16, 'customer', 'yay', 0, 1, '2025-11-04 05:17:32'),
(14, 1, 1, 'admin', 'why', 1, 1, '2025-11-04 05:18:09'),
(15, 1, 1, 'admin', 'what happened bella', 1, 1, '2025-11-04 05:18:25'),
(16, 1, 1, 'admin', 'why you cryin again', 1, 1, '2025-11-04 05:18:31'),
(17, 1, 16, 'customer', 'im so sorry', 0, 1, '2025-11-04 05:18:35'),
(18, 1, 16, 'customer', 'i\'m broken, my heart is shattered', 0, 1, '2025-11-04 05:19:01'),
(19, 1, 1, 'admin', 'oww', 1, 1, '2025-11-04 05:19:06'),
(20, 1, 1, 'admin', 'hayaan mo sila', 1, 1, '2025-11-04 05:19:13'),
(21, 1, 16, 'customer', 'ok', 0, 1, '2025-11-04 05:19:18'),
(22, 5, 16, 'customer', 'hey', 0, 0, '2025-11-20 21:46:31'),
(23, 6, 16, 'customer', 'uhm hello my order is not good', 0, 1, '2025-11-20 21:46:56'),
(24, 6, 8, 'seller', 'hello im so sorry', 0, 1, '2025-11-20 21:47:29'),
(25, 6, 16, 'customer', 'what are you sorry for? change it', 0, 1, '2025-11-20 21:53:07'),
(26, 6, 8, 'seller', 'okay wait haha', 0, 1, '2025-11-20 21:53:39'),
(27, 8, 16, 'customer', 'where\'s my order bro', 0, 0, '2025-11-21 03:35:43'),
(28, 7, 16, 'customer', 'yow', 0, 1, '2025-11-23 00:44:10'),
(29, 7, 1, 'admin', 'missu', 1, 1, '2025-11-23 00:44:46'),
(30, 15, 16, 'customer', 'hey where\'s my order at?!', 0, 1, '2025-11-26 08:10:12'),
(31, 11, 8, 'seller', 'hey', 0, 1, '2025-11-27 13:19:47'),
(32, 11, 1, 'admin', 'what\'s up?', 1, 1, '2025-11-27 13:20:14'),
(33, 11, 8, 'seller', 'i miss her bro', 0, 0, '2025-11-27 13:20:48'),
(34, 16, 16, 'customer', 'kuya wala po ako sa bahay hahaha', 0, 0, '2025-11-28 06:20:45');

-- --------------------------------------------------------

--
-- Table structure for table `chat_rooms`
--

CREATE TABLE `chat_rooms` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `participant1_id` int(11) DEFAULT NULL,
  `participant2_id` int(11) DEFAULT NULL,
  `conversation_type` enum('customer_admin','customer_seller','seller_admin','seller_rider','customer_rider') DEFAULT 'customer_admin',
  `related_order_id` int(11) DEFAULT NULL,
  `subject` varchar(255) NOT NULL DEFAULT 'Support Request',
  `status` enum('active','closed','archived') NOT NULL DEFAULT 'active',
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `chat_rooms`
--

INSERT INTO `chat_rooms` (`id`, `user_id`, `participant1_id`, `participant2_id`, `conversation_type`, `related_order_id`, `subject`, `status`, `created_at`, `updated_at`) VALUES
(1, 16, 16, NULL, 'customer_admin', NULL, 'Support Request', 'active', '2025-11-04 04:19:48', '2025-11-04 05:19:18'),
(2, 1, 1, NULL, 'customer_admin', NULL, 'Support Request', 'active', '2025-11-04 04:33:32', '2025-11-04 05:17:23'),
(3, 8, 8, NULL, 'customer_admin', NULL, 'Support Request', 'archived', '2025-11-08 01:36:41', '2025-11-26 08:28:01'),
(5, 16, 16, 8, 'customer_seller', NULL, 'Chat with Meow Shop', 'active', '2025-11-20 20:25:13', '2025-11-20 21:46:31'),
(6, 16, 16, 8, 'customer_seller', NULL, 'Order #46', 'active', '2025-11-20 21:46:42', '2025-11-20 21:53:39'),
(7, 16, 16, 1, 'customer_admin', NULL, 'Support Chat', 'active', '2025-11-20 22:12:15', '2025-11-23 00:44:46'),
(8, 16, 16, 8, 'customer_seller', 49, 'Order #49', 'active', '2025-11-20 23:35:02', '2025-11-21 03:35:43'),
(9, 16, 16, 8, 'customer_seller', 51, 'Order #51', 'archived', '2025-11-22 22:47:32', '2025-11-26 08:27:39'),
(10, 4, 4, 1, 'customer_admin', NULL, 'Support Chat', 'active', '2025-11-23 00:37:28', '2025-11-23 00:37:28'),
(11, 8, 8, 1, 'seller_admin', NULL, 'Chat with Admin', 'active', '2025-11-24 14:49:22', '2025-11-27 13:20:48'),
(12, 16, 16, 8, 'customer_seller', 52, 'Order #52', 'archived', '2025-11-24 15:34:58', '2025-11-26 08:27:34'),
(13, 16, 16, 1, 'customer_seller', 64, 'Order #PF-20251126-A77287A7', 'active', '2025-11-26 08:00:54', '2025-11-26 08:00:54'),
(14, 16, 16, 8, 'customer_seller', 62, 'Order #62', 'archived', '2025-11-26 08:07:30', '2025-11-26 08:27:30'),
(15, 16, 16, 8, 'customer_seller', 64, 'Order #PF-20251126-A77287A7', 'active', '2025-11-26 08:10:02', '2025-11-26 08:10:12'),
(16, 16, 16, 28, 'customer_rider', 72, 'Order #PF-20251128-C160D096 - Delivery', 'active', '2025-11-28 06:18:40', '2025-11-28 06:20:45');

-- --------------------------------------------------------

--
-- Table structure for table `deliveries`
--

CREATE TABLE `deliveries` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `assigned_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `picked_up_at` timestamp NULL DEFAULT NULL,
  `on_the_way_at` datetime DEFAULT NULL,
  `delivered_at` timestamp NULL DEFAULT NULL,
  `failed_at` datetime DEFAULT NULL,
  `delivery_notes` text DEFAULT NULL,
  `proof_photo_url` varchar(255) DEFAULT NULL,
  `signature_url` varchar(255) DEFAULT NULL,
  `recipient_name` varchar(150) DEFAULT NULL,
  `cod_collected` decimal(10,2) DEFAULT NULL,
  `delivered_lat` decimal(10,8) DEFAULT NULL,
  `delivered_lng` decimal(11,8) DEFAULT NULL,
  `pod_submitted_at` datetime DEFAULT NULL,
  `failure_reason` text DEFAULT NULL,
  `status` enum('assigned','picked_up','on_the_way','delivered','failed') DEFAULT 'assigned'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `deliveries`
--

INSERT INTO `deliveries` (`id`, `order_id`, `rider_id`, `assigned_at`, `picked_up_at`, `on_the_way_at`, `delivered_at`, `failed_at`, `delivery_notes`, `proof_photo_url`, `signature_url`, `recipient_name`, `cod_collected`, `delivered_lat`, `delivered_lng`, `pod_submitted_at`, `failure_reason`, `status`) VALUES
(20, 29, 4, '2025-11-02 08:16:24', '2025-11-03 20:34:59', NULL, NULL, '2025-11-20 01:41:43', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'nasira motor boss', 'failed'),
(26, 33, 4, '2025-11-03 06:25:42', NULL, NULL, NULL, '2025-11-04 01:12:32', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'wala ng gas, aguy', 'failed'),
(28, 37, 4, '2025-11-03 16:41:37', '2025-11-03 16:41:46', '2025-11-19 15:25:16', NULL, '2025-11-20 01:41:35', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'haha', 'failed'),
(29, 36, 4, '2025-11-10 23:39:19', '2025-11-10 23:41:38', '2025-11-11 07:45:17', '2025-11-10 23:46:25', NULL, NULL, 'uploads/pod/proof_29_1762789585.jpg', NULL, 'Kyla Conservado', 100.00, 14.23640540, 121.50487080, '2025-11-11 07:46:25', NULL, 'delivered'),
(31, 47, 4, '2025-11-19 16:18:19', '2025-11-19 16:18:36', '2025-11-20 00:19:43', '2025-11-19 16:20:08', NULL, NULL, 'uploads/pod/proof_31_1763540408.jpg', 'uploads/pod/sign_31_1763540408.png', 'Kyla Conservado', 129.00, 14.25332750, 121.50130160, '2025-11-20 00:20:08', NULL, 'delivered'),
(32, 48, 4, '2025-11-19 17:44:50', '2025-11-19 17:44:57', '2025-11-20 01:44:59', '2025-11-19 17:45:26', NULL, 'hindi ligo yung customer pre', 'uploads/pod/proof_32_1763545526.jpg', 'uploads/pod/sign_32_1763545526.png', 'Kyla Conservado', 2000.00, 14.25332750, 121.50130160, '2025-11-20 01:45:26', NULL, 'delivered'),
(33, 49, 4, '2025-11-20 15:08:53', '2025-11-20 15:09:02', '2025-11-24 19:30:46', '2025-11-24 11:31:25', NULL, NULL, 'uploads/pod/proof_33_1763955085.png', 'uploads/pod/sign_33_1763955085.png', 'Kyla Conservado', 400.00, 14.25244430, 121.50487080, '2025-11-24 19:31:25', NULL, 'delivered'),
(34, 51, 4, '2025-11-22 15:30:29', '2025-11-22 15:30:38', '2025-11-22 23:30:47', '2025-11-22 16:46:53', NULL, 'pangit nung receiver', 'uploads/pod/proof_34_1763801213.png', 'uploads/pod/sign_34_1763801213.png', 'Kyla Conservado', 1.13, 14.42763910, 120.93724290, '2025-11-23 00:46:53', NULL, 'delivered'),
(35, 50, 4, '2025-11-24 19:27:19', '2025-11-24 19:27:26', '2025-11-25 03:27:33', '2025-11-24 19:28:22', NULL, 'the receiver is not ligo', 'uploads/pod/proof_35_1763983701.png', 'uploads/pod/sign_35_1763983701.png', 'Kyla Conservado', 180.00, 14.25244430, 121.50487080, '2025-11-25 03:28:22', NULL, 'delivered'),
(36, 53, 4, '2025-11-24 19:49:57', '2025-11-24 19:50:03', '2025-11-25 03:50:07', '2025-11-24 19:50:42', NULL, 'miss q na siya', 'uploads/pod/proof_36_1763985042.png', 'uploads/pod/sign_36_1763985042.png', 'Kyla Conservado', 117.00, 14.25244430, 121.50487080, '2025-11-25 03:50:42', NULL, 'delivered'),
(37, 52, 4, '2025-11-24 20:45:36', '2025-11-24 20:45:43', '2025-11-26 09:33:38', '2025-11-26 01:36:19', NULL, NULL, 'uploads/pod/proof_37_1764092179.png', 'uploads/pod/sign_37_1764092179.png', 'Kyla Conservado', 162.00, 14.24412600, 121.51222200, '2025-11-26 09:36:19', NULL, 'delivered'),
(38, 64, 4, '2025-11-26 01:33:37', '2025-11-26 01:33:43', '2025-11-26 09:36:24', '2025-11-26 01:37:56', NULL, NULL, 'uploads/pod/proof_38_1764092276.png', 'uploads/pod/sign_38_1764092276.png', 'Kyla Conservado', 89.00, 14.24411625, 121.51216487, '2025-11-26 09:37:56', NULL, 'delivered'),
(39, 70, 26, '2025-11-26 14:03:07', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'assigned'),
(40, 72, 28, '2025-11-27 22:14:00', '2025-11-27 22:14:07', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'picked_up');

-- --------------------------------------------------------

--
-- Table structure for table `delivery_proofs`
--

CREATE TABLE `delivery_proofs` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `recipient_name` varchar(100) NOT NULL,
  `recipient_phone` varchar(20) DEFAULT NULL,
  `signature_image` varchar(255) NOT NULL,
  `proof_photo` varchar(255) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `cod_collected` decimal(10,2) DEFAULT NULL,
  `delivered_lat` decimal(10,8) DEFAULT NULL,
  `delivered_lng` decimal(11,8) DEFAULT NULL,
  `delivered_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `email_templates`
--

CREATE TABLE `email_templates` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `subject` varchar(255) NOT NULL,
  `html_content` text NOT NULL,
  `text_content` text DEFAULT NULL,
  `template_type` enum('notification','marketing','system','transaction') DEFAULT 'notification',
  `variables` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `inventory_transactions`
--

CREATE TABLE `inventory_transactions` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `transaction_type` enum('purchase','sale','return','adjustment','restock') NOT NULL,
  `quantity` int(11) NOT NULL,
  `previous_stock` int(11) NOT NULL,
  `new_stock` int(11) NOT NULL,
  `reference_type` enum('order','return_request','manual') NOT NULL,
  `reference_id` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `inventory_transactions`
--

INSERT INTO `inventory_transactions` (`id`, `product_id`, `transaction_type`, `quantity`, `previous_stock`, `new_stock`, `reference_type`, `reference_id`, `notes`, `created_by`, `created_at`) VALUES
(1, 19, 'sale', 13, 70, 57, 'order', 39, NULL, NULL, '2025-11-03 19:38:32'),
(2, 19, 'sale', 3, 57, 54, 'order', 40, NULL, NULL, '2025-11-03 21:42:44'),
(3, 25, 'sale', 1, 120, 119, 'order', 41, NULL, NULL, '2025-11-04 05:00:54'),
(4, 19, 'sale', 1, 54, 53, 'order', 42, NULL, NULL, '2025-11-04 05:50:06'),
(5, 23, 'sale', 2, 100, 98, 'order', 43, NULL, NULL, '2025-11-07 17:39:33'),
(6, 26, 'sale', 5, 100, 95, 'order', 43, NULL, NULL, '2025-11-07 17:39:33'),
(7, 26, 'sale', 8, 95, 87, 'order', 44, NULL, NULL, '2025-11-12 02:36:40'),
(8, 23, 'sale', 1, 98, 97, 'order', 45, NULL, NULL, '2025-11-13 15:26:50'),
(9, 26, 'sale', 5, 87, 82, 'order', 45, NULL, NULL, '2025-11-13 15:26:50'),
(10, 26, 'sale', 2, 82, 80, 'order', 46, NULL, NULL, '2025-11-13 15:37:14'),
(11, 24, 'sale', 1, 45, 44, 'order', 47, NULL, NULL, '2025-11-19 16:17:01'),
(12, 25, 'sale', 1, 119, 118, 'order', 47, NULL, NULL, '2025-11-19 16:17:01'),
(13, 26, 'sale', 80, 80, 0, 'order', 48, NULL, NULL, '2025-11-19 17:12:48'),
(14, 24, 'sale', 44, 44, 0, 'order', 49, NULL, NULL, '2025-11-20 15:05:13'),
(15, 25, 'sale', 4, 118, 114, 'order', 50, NULL, NULL, '2025-11-21 18:21:05'),
(16, 25, 'sale', 1, 114, 113, 'order', 51, NULL, NULL, '2025-11-21 18:36:32'),
(17, 95, 'sale', 2, 6, 4, 'order', 52, NULL, NULL, '2025-11-24 07:34:31'),
(18, 25, 'sale', 1, 113, 112, 'order', 52, NULL, NULL, '2025-11-24 07:34:31'),
(19, 95, 'sale', 2, 7, 5, 'order', 53, NULL, NULL, '2025-11-24 11:08:30'),
(20, 62, 'sale', 5, 92, 87, 'order', 60, NULL, NULL, '2025-11-25 08:45:27'),
(21, 96, 'sale', 1, 11, 10, 'order', 61, NULL, NULL, '2025-11-25 09:33:26'),
(22, 83, 'sale', 1, 6, 5, 'order', 62, NULL, NULL, '2025-11-25 10:05:18'),
(23, 94, 'sale', 4, 50, 46, 'order', 63, NULL, NULL, '2025-11-25 10:18:12'),
(24, 95, 'sale', 1, 4, 3, 'order', 64, NULL, NULL, '2025-11-26 00:00:44'),
(25, 93, 'sale', 1, 5, 4, 'order', 65, NULL, NULL, '2025-11-26 12:44:56'),
(26, 94, 'sale', 2, 52, 50, 'order', 66, NULL, NULL, '2025-11-26 13:05:59'),
(27, 19, 'sale', 2, 53, 51, 'order', 67, NULL, NULL, '2025-11-26 13:20:13'),
(28, 20, 'sale', 4, 64, 60, 'order', 67, NULL, NULL, '2025-11-26 13:20:13'),
(29, 19, 'sale', 4, 51, 47, 'order', 68, NULL, NULL, '2025-11-26 13:21:06'),
(30, 20, 'sale', 8, 60, 52, 'order', 68, NULL, NULL, '2025-11-26 13:21:06'),
(31, 94, 'sale', 1, 53, 52, 'order', 69, NULL, NULL, '2025-11-26 13:21:34'),
(32, 91, 'sale', 1, 51, 50, 'order', 70, NULL, NULL, '2025-11-26 13:31:49'),
(33, 88, 'sale', 1, 83, 82, 'order', 71, NULL, NULL, '2025-11-27 05:25:59'),
(34, 84, 'sale', 1, 75, 74, 'order', 72, NULL, NULL, '2025-11-27 22:02:25');

-- --------------------------------------------------------

--
-- Table structure for table `low_stock_alerts`
--

CREATE TABLE `low_stock_alerts` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `threshold_quantity` int(11) NOT NULL DEFAULT 10,
  `current_stock` int(11) NOT NULL,
  `alert_sent` tinyint(1) DEFAULT 0,
  `alert_sent_at` timestamp NULL DEFAULT NULL,
  `acknowledged` tinyint(1) DEFAULT 0,
  `acknowledged_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `low_stock_alerts`
--

INSERT INTO `low_stock_alerts` (`id`, `product_id`, `seller_id`, `threshold_quantity`, `current_stock`, `alert_sent`, `alert_sent_at`, `acknowledged`, `acknowledged_at`, `created_at`) VALUES
(1, 26, 8, 10, 80, 0, NULL, 1, '2025-11-19 17:13:41', '2025-11-19 17:12:48'),
(2, 24, 8, 10, 44, 0, NULL, 0, NULL, '2025-11-20 15:05:13'),
(3, 95, 8, 10, 6, 0, NULL, 0, NULL, '2025-11-24 07:34:31'),
(4, 95, 8, 10, 7, 0, NULL, 0, NULL, '2025-11-24 11:08:30'),
(5, 96, 8, 10, 11, 0, NULL, 0, NULL, '2025-11-25 09:33:26'),
(6, 83, 8, 10, 6, 0, NULL, 0, NULL, '2025-11-25 10:05:18'),
(7, 95, 8, 10, 4, 0, NULL, 0, NULL, '2025-11-26 00:00:44'),
(8, 93, 8, 10, 5, 0, NULL, 0, NULL, '2025-11-26 12:44:56');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `type` enum('order_status','seller_application','product_review','delivery_update','general') NOT NULL,
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `related_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `role` enum('admin','seller','user','rider') NOT NULL DEFAULT 'user',
  `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`data`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `type`, `title`, `message`, `is_read`, `related_id`, `created_at`, `role`, `data`) VALUES
(1, 16, 'order_status', 'Order confirmed', 'Your order #37 is confirmed.', 1, 37, '2025-11-04 00:26:01', 'user', '{\"order_id\": 37, \"status\": \"confirmed\"}'),
(2, 16, 'order_status', 'Order confirmed', 'Your order #37 is confirmed.', 1, 37, '2025-11-04 00:40:53', 'user', '{\"order_id\": 37, \"status\": \"confirmed\"}'),
(3, 16, 'order_status', 'Order picked up', 'Your order #37 has been picked up by the rider.', 1, 37, '2025-11-04 00:41:46', 'user', '{\"order_id\": 37, \"status\": \"picked_up\", \"delivery_id\": 28}'),
(4, 8, 'order_status', 'Order picked up', 'Order #37: Your order #37 has been picked up by the rider.', 1, 37, '2025-11-04 00:41:46', 'seller', '{\"order_id\": 37, \"status\": \"picked_up\", \"delivery_id\": 28}'),
(5, 16, 'order_status', 'Delivery failed', 'Delivery for order #33 has failed. Reason: wala ng gas, aguy', 1, 33, '2025-11-04 01:12:32', 'user', '{\"order_id\": 33, \"status\": \"failed\", \"delivery_id\": 26}'),
(6, 8, 'order_status', 'Delivery failed', 'Order #33: Delivery for order #33 has failed. Reason: wala ng gas, aguy', 0, 33, '2025-11-04 01:12:32', 'seller', '{\"order_id\": 33, \"status\": \"failed\", \"delivery_id\": 26}'),
(7, 16, 'order_status', 'Order preparing', 'Your order #39 is preparing.', 1, 39, '2025-11-04 03:39:56', 'user', '{\"order_id\": 39, \"status\": \"preparing\"}'),
(8, 16, 'order_status', 'Order picked up', 'Your order #29 has been picked up by the rider.', 1, 29, '2025-11-04 04:34:59', 'user', '{\"order_id\": 29, \"status\": \"picked_up\", \"delivery_id\": 20}'),
(10, 16, 'order_status', 'Order preparing', 'Your order #40 is preparing.', 1, 40, '2025-11-04 05:43:30', 'user', '{\"order_id\": 40, \"status\": \"preparing\"}'),
(11, 16, 'order_status', 'Order picked up', 'Your order #36 has been picked up by the rider.', 1, 36, '2025-11-11 07:41:38', 'user', '{\"order_id\": 36, \"status\": \"picked_up\", \"delivery_id\": 29}'),
(12, 8, 'order_status', 'Order picked up', 'Order #36: Your order #36 has been picked up by the rider.', 0, 36, '2025-11-11 07:41:38', 'seller', '{\"order_id\": 36, \"status\": \"picked_up\", \"delivery_id\": 29}'),
(13, 16, 'order_status', 'Order confirmed', 'Your order #43 is confirmed.', 1, 43, '2025-11-11 07:43:20', 'user', '{\"order_id\": 43, \"status\": \"confirmed\"}'),
(14, 16, 'order_status', 'Order preparing', 'Your order #43 is preparing.', 1, 43, '2025-11-11 07:43:43', 'user', '{\"order_id\": 43, \"status\": \"preparing\"}'),
(15, 16, 'order_status', 'Order on the way', 'Your order #36 is now on the way.', 1, 36, '2025-11-11 07:45:17', 'user', '{\"order_id\": 36, \"status\": \"on_the_way\", \"delivery_id\": 29}'),
(16, 8, 'order_status', 'Order on the way', 'Order #36: Your order #36 is now on the way.', 0, 36, '2025-11-11 07:45:17', 'seller', '{\"order_id\": 36, \"status\": \"on_the_way\", \"delivery_id\": 29}'),
(17, 16, 'order_status', 'Order delivered', 'Your order #36 has been delivered.', 1, 36, '2025-11-11 07:46:25', 'user', '{\"order_id\": 36, \"status\": \"delivered\", \"delivery_id\": 29}'),
(18, 8, 'order_status', 'Order delivered', 'Order #36: Your order #36 has been delivered.', 0, 36, '2025-11-11 07:46:25', 'seller', '{\"order_id\": 36, \"status\": \"delivered\", \"delivery_id\": 29}'),
(19, 16, 'order_status', 'Order confirmed', 'Your order #43 is confirmed.', 1, 43, '2025-11-11 18:16:18', 'user', '{\"order_id\": 43, \"status\": \"confirmed\"}'),
(20, 16, 'order_status', 'Order on the way', 'Your order #43 is now on the way.', 1, 43, '2025-11-11 18:17:12', 'user', '{\"order_id\": 43, \"status\": \"on_the_way\", \"delivery_id\": 30}'),
(21, 8, 'order_status', 'Order on the way', 'Order #43: Your order #43 is now on the way.', 0, 43, '2025-11-11 18:17:12', 'seller', '{\"order_id\": 43, \"status\": \"on_the_way\", \"delivery_id\": 30}'),
(22, 16, 'order_status', 'Order preparing', 'Your order #44 is preparing.', 1, 44, '2025-11-12 10:37:25', 'user', '{\"order_id\": 44, \"status\": \"preparing\"}'),
(23, 16, 'order_status', 'Order confirmed', 'Your order #44 is confirmed.', 1, 44, '2025-11-12 10:37:32', 'user', '{\"order_id\": 44, \"status\": \"confirmed\"}'),
(24, 16, 'order_status', 'Order delivered', 'Your order #43 has been delivered.', 1, 43, '2025-11-14 20:36:42', 'user', '{\"order_id\": 43, \"status\": \"delivered\", \"delivery_id\": 30}'),
(25, 8, 'order_status', 'Order delivered', 'Order #43: Your order #43 has been delivered.', 0, 43, '2025-11-14 20:36:42', 'seller', '{\"order_id\": 43, \"status\": \"delivered\", \"delivery_id\": 30}'),
(26, 16, 'order_status', 'Order on the way', 'Your order #37 is now on the way.', 1, 37, '2025-11-19 15:25:16', 'user', '{\"order_id\": 37, \"status\": \"on_the_way\", \"delivery_id\": 28}'),
(27, 8, 'order_status', 'Order on the way', 'Order #37: Your order #37 is now on the way.', 0, 37, '2025-11-19 15:25:16', 'seller', '{\"order_id\": 37, \"status\": \"on_the_way\", \"delivery_id\": 28}'),
(28, 16, 'order_status', 'Order confirmed', 'Your order #47 is confirmed.', 1, 47, '2025-11-20 00:17:31', 'user', '{\"order_id\": 47, \"status\": \"confirmed\"}'),
(29, 16, 'order_status', 'Order picked up', 'Your order #47 has been picked up by the rider.', 1, 47, '2025-11-20 00:18:36', 'user', '{\"order_id\": 47, \"status\": \"picked_up\", \"delivery_id\": 31}'),
(30, 8, 'order_status', 'Order picked up', 'Order #47: Your order #47 has been picked up by the rider.', 0, 47, '2025-11-20 00:18:36', 'seller', '{\"order_id\": 47, \"status\": \"picked_up\", \"delivery_id\": 31}'),
(31, 16, 'order_status', 'Order on the way', 'Your order #47 is now on the way.', 1, 47, '2025-11-20 00:19:43', 'user', '{\"order_id\": 47, \"status\": \"on_the_way\", \"delivery_id\": 31}'),
(32, 8, 'order_status', 'Order on the way', 'Order #47: Your order #47 is now on the way.', 0, 47, '2025-11-20 00:19:43', 'seller', '{\"order_id\": 47, \"status\": \"on_the_way\", \"delivery_id\": 31}'),
(33, 16, 'order_status', 'Order delivered', 'Your order #47 has been delivered.', 1, 47, '2025-11-20 00:20:08', 'user', '{\"order_id\": 47, \"status\": \"delivered\", \"delivery_id\": 31}'),
(34, 8, 'order_status', 'Order delivered', 'Order #47: Your order #47 has been delivered.', 0, 47, '2025-11-20 00:20:08', 'seller', '{\"order_id\": 47, \"status\": \"delivered\", \"delivery_id\": 31}'),
(35, 8, '', 'New order received', 'You have a new order #48 totaling ₱3,000.00.', 0, 48, '2025-11-20 01:12:48', 'seller', '{\"order_id\": 48, \"total_amount\": 3000.0, \"item_count\": 1}'),
(36, 16, 'order_status', 'Order confirmed', 'Your order #48 is confirmed.', 1, 48, '2025-11-20 01:14:22', 'user', '{\"order_id\": 48, \"status\": \"confirmed\"}'),
(37, 16, 'order_status', 'Order preparing', 'Your order #48 is preparing.', 1, 48, '2025-11-20 01:40:52', 'user', '{\"order_id\": 48, \"status\": \"preparing\"}'),
(38, 16, 'order_status', 'Delivery failed', 'Delivery for order #37 has failed. Reason: haha', 1, 37, '2025-11-20 01:41:35', 'user', '{\"order_id\": 37, \"status\": \"failed\", \"delivery_id\": 28}'),
(39, 8, 'order_status', 'Delivery failed', 'Order #37: Delivery for order #37 has failed. Reason: haha', 0, 37, '2025-11-20 01:41:35', 'seller', '{\"order_id\": 37, \"status\": \"failed\", \"delivery_id\": 28}'),
(40, 16, 'order_status', 'Delivery failed', 'Delivery for order #29 has failed. Reason: nasira motor boss', 1, 29, '2025-11-20 01:41:43', 'user', '{\"order_id\": 29, \"status\": \"failed\", \"delivery_id\": 20}'),
(42, 16, 'order_status', 'Order picked up', 'Your order #48 has been picked up by the rider.', 1, 48, '2025-11-20 01:44:57', 'user', '{\"order_id\": 48, \"status\": \"picked_up\", \"delivery_id\": 32}'),
(43, 8, 'order_status', 'Order picked up', 'Order #48: Your order #48 has been picked up by the rider.', 0, 48, '2025-11-20 01:44:57', 'seller', '{\"order_id\": 48, \"status\": \"picked_up\", \"delivery_id\": 32}'),
(44, 16, 'order_status', 'Order on the way', 'Your order #48 is now on the way.', 1, 48, '2025-11-20 01:44:59', 'user', '{\"order_id\": 48, \"status\": \"on_the_way\", \"delivery_id\": 32}'),
(45, 8, 'order_status', 'Order on the way', 'Order #48: Your order #48 is now on the way.', 0, 48, '2025-11-20 01:44:59', 'seller', '{\"order_id\": 48, \"status\": \"on_the_way\", \"delivery_id\": 32}'),
(46, 16, 'order_status', 'Order delivered', 'Your order #48 has been delivered.', 1, 48, '2025-11-20 01:45:26', 'user', '{\"order_id\": 48, \"status\": \"delivered\", \"delivery_id\": 32}'),
(47, 8, 'order_status', 'Order delivered', 'Order #48: Your order #48 has been delivered.', 0, 48, '2025-11-20 01:45:26', 'seller', '{\"order_id\": 48, \"status\": \"delivered\", \"delivery_id\": 32}'),
(48, 8, '', 'New message from Kyla Conservado', 'hey', 0, 5, '2025-11-20 21:46:31', 'seller', '{\"room_id\": 5, \"from_user_id\": 16}'),
(49, 8, '', 'New message from Kyla Conservado', 'uhm hello my order is not good', 0, 6, '2025-11-20 21:46:56', 'seller', '{\"room_id\": 6, \"from_user_id\": 16}'),
(50, 16, '', 'New message from Meow Shop', 'hello im so sorry', 1, 6, '2025-11-20 21:47:29', 'user', '{\"room_id\": 6, \"from_user_id\": 8}'),
(51, 8, '', 'New message from Kyla Conservado', 'what are you sorry for? change it', 0, 6, '2025-11-20 21:53:07', 'seller', '{\"room_id\": 6, \"from_user_id\": 16}'),
(52, 16, '', 'New message from Meow Shop', 'okay wait haha', 1, 6, '2025-11-20 21:53:39', 'user', '{\"room_id\": 6, \"from_user_id\": 8}'),
(53, 8, '', 'New order received', 'You have a new order #49 totaling ₱3,696.00.', 0, 49, '2025-11-20 23:05:13', 'seller', '{\"order_id\": 49, \"total_amount\": 3696.0, \"item_count\": 1}'),
(54, 16, 'order_status', 'Order preparing', 'Your order #49 is preparing.', 1, 49, '2025-11-20 23:08:06', 'user', '{\"order_id\": 49, \"status\": \"preparing\"}'),
(55, 16, 'order_status', 'Order confirmed', 'Your order #49 is confirmed.', 1, 49, '2025-11-20 23:08:13', 'user', '{\"order_id\": 49, \"status\": \"confirmed\"}'),
(56, 16, 'order_status', 'Order picked up', 'Your order #49 has been picked up by the rider.', 1, 49, '2025-11-20 23:09:02', 'user', '{\"order_id\": 49, \"status\": \"picked_up\", \"delivery_id\": 33}'),
(57, 8, 'order_status', 'Order picked up', 'Order #49: Your order #49 has been picked up by the rider.', 0, 49, '2025-11-20 23:09:02', 'seller', '{\"order_id\": 49, \"status\": \"picked_up\", \"delivery_id\": 33}'),
(58, 16, 'order_status', 'Order on the way', 'Your order #49 is now on the way.', 0, 49, '2025-11-20 23:13:49', 'user', '{\"order_id\": 49, \"status\": \"on_the_way\", \"delivery_id\": 33}'),
(59, 8, 'order_status', 'Order on the way', 'Order #49: Your order #49 is now on the way.', 0, 49, '2025-11-20 23:13:49', 'seller', '{\"order_id\": 49, \"status\": \"on_the_way\", \"delivery_id\": 33}'),
(60, 8, '', 'New message from Kyla Conservado', 'where\'s my order bro', 0, 8, '2025-11-21 03:35:43', 'seller', '{\"room_id\": 8, \"from_user_id\": 16}'),
(61, 8, '', 'New order received', 'You have a new order #50 totaling ₱180.00.', 0, 50, '2025-11-22 02:21:05', 'seller', '{\"order_id\": 50, \"total_amount\": 180.0, \"item_count\": 1}'),
(62, 16, 'order_status', 'Order preparing', 'Your order #50 is preparing.', 0, 50, '2025-11-22 02:21:36', 'user', '{\"order_id\": 50, \"status\": \"preparing\"}'),
(63, 8, '', 'New order received', 'You have a new order #51 totaling ₱45.00.', 0, 51, '2025-11-22 02:36:32', 'seller', '{\"order_id\": 51, \"total_amount\": 45.0, \"item_count\": 1}'),
(64, 16, 'order_status', 'Order preparing', 'Your order #51 is preparing.', 0, 51, '2025-11-22 23:29:51', 'user', '{\"order_id\": 51, \"status\": \"preparing\"}'),
(65, 16, 'order_status', 'Order picked up', 'Your order #51 has been picked up by the rider.', 0, 51, '2025-11-22 23:30:38', 'user', '{\"order_id\": 51, \"status\": \"picked_up\", \"delivery_id\": 34}'),
(66, 8, 'order_status', 'Order picked up', 'Order #51: Your order #51 has been picked up by the rider.', 0, 51, '2025-11-22 23:30:38', 'seller', '{\"order_id\": 51, \"status\": \"picked_up\", \"delivery_id\": 34}'),
(67, 16, 'order_status', 'Order on the way', 'Your order #51 is now on the way.', 0, 51, '2025-11-22 23:30:47', 'user', '{\"order_id\": 51, \"status\": \"on_the_way\", \"delivery_id\": 34}'),
(68, 8, 'order_status', 'Order on the way', 'Order #51: Your order #51 is now on the way.', 0, 51, '2025-11-22 23:30:47', 'seller', '{\"order_id\": 51, \"status\": \"on_the_way\", \"delivery_id\": 34}'),
(69, 1, '', 'New message from Kyla Conservado', 'yow', 0, 7, '2025-11-23 00:44:10', 'admin', '{\"room_id\": 7, \"from_user_id\": 16}'),
(70, 16, '', 'New message from Admin User', 'missu', 0, 7, '2025-11-23 00:44:46', 'user', '{\"room_id\": 7, \"from_user_id\": 1}'),
(71, 16, 'order_status', 'Order delivered', 'Your order #51 has been delivered.', 0, 51, '2025-11-23 00:46:53', 'user', '{\"order_id\": 51, \"status\": \"delivered\", \"delivery_id\": 34}'),
(72, 8, 'order_status', 'Order delivered', 'Order #51: Your order #51 has been delivered.', 0, 51, '2025-11-23 00:46:53', 'seller', '{\"order_id\": 51, \"status\": \"delivered\", \"delivery_id\": 34}'),
(73, 8, '', 'New order received', 'You have a new order #52 totaling ₱162.00.', 0, 52, '2025-11-24 15:34:31', 'seller', '{\"order_id\": 52, \"total_amount\": 162.0, \"item_count\": 2}'),
(74, 8, '', 'New order received', 'You have a new order #53 totaling ₱117.00.', 0, 53, '2025-11-24 19:08:30', 'seller', '{\"order_id\": 53, \"total_amount\": 117.0, \"item_count\": 1}'),
(75, 16, 'order_status', 'Order delivered', 'Your order #49 has been delivered.', 0, 49, '2025-11-24 19:31:25', 'user', '{\"order_id\": 49, \"status\": \"delivered\", \"delivery_id\": 33}'),
(76, 8, 'order_status', 'Order delivered', 'Order #49: Your order #49 has been delivered.', 0, 49, '2025-11-24 19:31:25', 'seller', '{\"order_id\": 49, \"status\": \"delivered\", \"delivery_id\": 33}'),
(77, 16, 'order_status', 'Order picked up', 'Your order #50 has been picked up by the rider.', 0, 50, '2025-11-25 03:27:26', 'user', '{\"order_id\": 50, \"status\": \"picked_up\", \"delivery_id\": 35}'),
(78, 8, 'order_status', 'Order picked up', 'Order #50: Your order #50 has been picked up by the rider.', 0, 50, '2025-11-25 03:27:26', 'seller', '{\"order_id\": 50, \"status\": \"picked_up\", \"delivery_id\": 35}'),
(79, 16, 'order_status', 'Order on the way', 'Your order #50 is now on the way.', 0, 50, '2025-11-25 03:27:33', 'user', '{\"order_id\": 50, \"status\": \"on_the_way\", \"delivery_id\": 35}'),
(80, 8, 'order_status', 'Order on the way', 'Order #50: Your order #50 is now on the way.', 0, 50, '2025-11-25 03:27:33', 'seller', '{\"order_id\": 50, \"status\": \"on_the_way\", \"delivery_id\": 35}'),
(81, 16, 'order_status', 'Order delivered', 'Your order #50 has been delivered.', 0, 50, '2025-11-25 03:28:22', 'user', '{\"order_id\": 50, \"status\": \"delivered\", \"delivery_id\": 35}'),
(82, 8, 'order_status', 'Order delivered', 'Order #50: Your order #50 has been delivered.', 0, 50, '2025-11-25 03:28:22', 'seller', '{\"order_id\": 50, \"status\": \"delivered\", \"delivery_id\": 35}'),
(83, 16, 'order_status', 'Order confirmed', 'Your order #53 is confirmed.', 0, 53, '2025-11-25 03:48:43', 'user', '{\"order_id\": 53, \"status\": \"confirmed\"}'),
(84, 16, 'order_status', 'Order preparing', 'Your order #52 is preparing.', 0, 52, '2025-11-25 03:48:54', 'user', '{\"order_id\": 52, \"status\": \"preparing\"}'),
(85, 16, 'order_status', 'Order picked up', 'Your order #53 has been picked up by the rider.', 0, 53, '2025-11-25 03:50:03', 'user', '{\"order_id\": 53, \"status\": \"picked_up\", \"delivery_id\": 36}'),
(86, 8, 'order_status', 'Order picked up', 'Order #53: Your order #53 has been picked up by the rider.', 0, 53, '2025-11-25 03:50:03', 'seller', '{\"order_id\": 53, \"status\": \"picked_up\", \"delivery_id\": 36}'),
(87, 16, 'order_status', 'Order on the way', 'Your order #53 is now on the way.', 0, 53, '2025-11-25 03:50:05', 'user', '{\"order_id\": 53, \"status\": \"on_the_way\", \"delivery_id\": 36}'),
(88, 8, 'order_status', 'Order on the way', 'Order #53: Your order #53 is now on the way.', 0, 53, '2025-11-25 03:50:05', 'seller', '{\"order_id\": 53, \"status\": \"on_the_way\", \"delivery_id\": 36}'),
(89, 16, 'order_status', 'Order on the way', 'Your order #53 is now on the way.', 0, 53, '2025-11-25 03:50:07', 'user', '{\"order_id\": 53, \"status\": \"on_the_way\", \"delivery_id\": 36}'),
(90, 8, 'order_status', 'Order on the way', 'Order #53: Your order #53 is now on the way.', 0, 53, '2025-11-25 03:50:07', 'seller', '{\"order_id\": 53, \"status\": \"on_the_way\", \"delivery_id\": 36}'),
(91, 16, 'order_status', 'Order delivered', 'Your order #53 has been delivered.', 0, 53, '2025-11-25 03:50:42', 'user', '{\"order_id\": 53, \"status\": \"delivered\", \"delivery_id\": 36}'),
(92, 8, 'order_status', 'Order delivered', 'Order #53: Your order #53 has been delivered.', 0, 53, '2025-11-25 03:50:42', 'seller', '{\"order_id\": 53, \"status\": \"delivered\", \"delivery_id\": 36}'),
(93, 16, 'order_status', 'Order picked up', 'Your order #52 has been picked up by the rider.', 0, 52, '2025-11-25 04:45:43', 'user', '{\"order_id\": 52, \"status\": \"picked_up\", \"delivery_id\": 37}'),
(94, 8, 'order_status', 'Order picked up', 'Order #52: Your order #52 has been picked up by the rider.', 0, 52, '2025-11-25 04:45:43', 'seller', '{\"order_id\": 52, \"status\": \"picked_up\", \"delivery_id\": 37}'),
(95, 16, 'order_status', 'Order on the way', 'Your order #52 is now on the way.', 0, 52, '2025-11-25 04:45:44', 'user', '{\"order_id\": 52, \"status\": \"on_the_way\", \"delivery_id\": 37}'),
(96, 8, 'order_status', 'Order on the way', 'Order #52: Your order #52 is now on the way.', 0, 52, '2025-11-25 04:45:44', 'seller', '{\"order_id\": 52, \"status\": \"on_the_way\", \"delivery_id\": 37}'),
(102, 16, 'order_status', 'Order Placed Successfully', 'Your order PF-20251125-E99ED70C has been placed successfully.', 0, 60, '2025-11-25 08:45:27', 'user', NULL),
(103, 16, 'order_status', 'Order Placed Successfully', 'Your order PF-20251125-1EA99DF4 has been placed successfully.', 0, 61, '2025-11-25 09:33:26', 'user', NULL),
(104, 16, 'order_status', 'Order Placed Successfully', 'Your order PF-20251125-3BFE473C has been placed successfully.', 0, 62, '2025-11-25 10:05:18', 'user', NULL),
(105, 16, 'order_status', 'Order Placed Successfully', 'Your order PF-20251125-7DD7EE06 has been placed successfully.', 0, 63, '2025-11-25 10:18:12', 'user', NULL),
(106, 16, 'order_status', 'Order preparing', 'Your order #63 is preparing.', 0, 63, '2025-11-25 18:58:53', 'user', '{\"order_id\": 63, \"status\": \"preparing\"}'),
(107, 16, 'order_status', 'Order confirmed', 'Your order #63 is confirmed.', 0, 63, '2025-11-25 18:59:01', 'user', '{\"order_id\": 63, \"status\": \"confirmed\"}'),
(108, 16, 'order_status', 'Order Placed Successfully', 'Your order PF-20251126-A77287A7 has been placed successfully.', 0, 64, '2025-11-26 00:00:44', 'user', NULL),
(109, 8, '', 'New message from Kyla Conservado', 'hey where\'s my order at?!', 0, 15, '2025-11-26 08:10:12', 'seller', '{\"room_id\": 15, \"from_user_id\": 16}'),
(110, 16, 'order_status', 'Order confirmed', 'Your order #64 is confirmed.', 0, 64, '2025-11-26 09:33:14', 'user', '{\"order_id\": 64, \"status\": \"confirmed\"}'),
(111, 16, 'order_status', 'Order picked up', 'Your order #64 has been picked up by the rider.', 0, 64, '2025-11-26 09:33:43', 'user', '{\"order_id\": 64, \"status\": \"picked_up\", \"delivery_id\": 38}'),
(112, 1, 'order_status', 'Order picked up', 'Order #64: Your order #64 has been picked up by the rider.', 0, 64, '2025-11-26 09:33:43', 'seller', '{\"order_id\": 64, \"status\": \"picked_up\", \"delivery_id\": 38}'),
(113, 16, 'order_status', 'Order delivered', 'Your order #52 has been delivered.', 0, 52, '2025-11-26 09:36:19', 'user', '{\"order_id\": 52, \"status\": \"delivered\", \"delivery_id\": 37}'),
(114, 1, 'order_status', 'Order delivered', 'Order #52: Your order #52 has been delivered.', 0, 52, '2025-11-26 09:36:19', 'seller', '{\"order_id\": 52, \"status\": \"delivered\", \"delivery_id\": 37}'),
(115, 16, 'order_status', 'Order on the way', 'Your order #64 is now on the way.', 0, 64, '2025-11-26 09:36:24', 'user', '{\"order_id\": 64, \"status\": \"on_the_way\", \"delivery_id\": 38}'),
(116, 1, 'order_status', 'Order on the way', 'Order #64: Your order #64 is now on the way.', 0, 64, '2025-11-26 09:36:24', 'seller', '{\"order_id\": 64, \"status\": \"on_the_way\", \"delivery_id\": 38}'),
(117, 16, 'order_status', 'Order delivered', 'Your order #64 has been delivered.', 0, 64, '2025-11-26 09:37:56', 'user', '{\"order_id\": 64, \"status\": \"delivered\", \"delivery_id\": 38}'),
(118, 1, 'order_status', 'Order delivered', 'Order #64: Your order #64 has been delivered.', 0, 64, '2025-11-26 09:37:56', 'seller', '{\"order_id\": 64, \"status\": \"delivered\", \"delivery_id\": 38}'),
(119, 25, 'order_status', 'Order Placed Successfully', 'Your order PF-20251126-5B39E145 has been placed successfully.', 0, 65, '2025-11-26 12:44:56', 'user', NULL),
(120, 25, 'order_status', 'Order Placed Successfully', 'Your order PF-20251126-615D4440 has been placed successfully.', 0, 66, '2025-11-26 13:05:59', 'user', NULL),
(121, 8, '', 'New order received', 'You have a new order #67 totaling ₱504.00.', 0, 67, '2025-11-26 21:20:13', 'seller', '{\"order_id\": 67, \"total_amount\": 504.0, \"item_count\": 2}'),
(122, 8, '', 'New order received', 'You have a new order #68 totaling ₱1,008.00.', 0, 68, '2025-11-26 21:21:06', 'seller', '{\"order_id\": 68, \"total_amount\": 1008.0, \"item_count\": 2}'),
(123, 25, 'order_status', 'Order Placed Successfully', 'Your order PF-20251126-F9FCB517 has been placed successfully.', 0, 69, '2025-11-26 13:21:34', 'user', NULL),
(124, 25, 'order_status', 'Order Placed Successfully', 'Your order PF-20251126-83888BF4 has been placed successfully.', 0, 70, '2025-11-26 13:31:49', 'user', NULL),
(125, 25, 'order_status', 'Order preparing', 'Your order #70 is preparing.', 0, 70, '2025-11-26 21:32:12', 'user', '{\"order_id\": 70, \"status\": \"preparing\"}'),
(126, 1, '', 'New message from Meow Shop', 'hey', 0, 11, '2025-11-27 13:19:47', 'admin', '{\"room_id\": 11, \"from_user_id\": 8}'),
(127, 8, '', 'New message from Admin User', 'what\'s up?', 0, 11, '2025-11-27 13:20:15', 'seller', '{\"room_id\": 11, \"from_user_id\": 1}'),
(128, 1, '', 'New message from Meow Shop', 'i miss her bro', 0, 11, '2025-11-27 13:20:48', 'admin', '{\"room_id\": 11, \"from_user_id\": 8}'),
(129, 16, 'order_status', 'Order Placed Successfully', 'Your order PF-20251127-17CEC559 has been placed successfully.', 0, 71, '2025-11-27 05:25:59', 'user', NULL),
(130, 16, 'order_status', 'Order preparing', 'Your order #71 is preparing.', 0, 71, '2025-11-27 13:26:28', 'user', '{\"order_id\": 71, \"status\": \"preparing\"}'),
(131, 16, 'order_status', 'Order Placed Successfully', 'Your order PF-20251128-C160D096 has been placed successfully.', 0, 72, '2025-11-27 22:02:25', 'user', NULL),
(132, 16, 'order_status', 'Order preparing', 'Your order #72 is preparing.', 0, 72, '2025-11-28 06:04:44', 'user', '{\"order_id\": 72, \"status\": \"preparing\"}'),
(133, 16, 'order_status', 'Order picked up', 'Your order #72 has been picked up by the rider.', 0, 72, '2025-11-28 06:14:07', 'user', '{\"order_id\": 72, \"status\": \"picked_up\", \"delivery_id\": 40}'),
(134, 1, 'order_status', 'Order picked up', 'Order #72: Your order #72 has been picked up by the rider.', 0, 72, '2025-11-28 06:14:07', 'seller', '{\"order_id\": 72, \"status\": \"picked_up\", \"delivery_id\": 40}'),
(135, 28, '', 'New message from Kyla Conservado', 'kuya wala po ako sa bahay hahaha', 0, 16, '2025-11-28 06:20:45', 'rider', '{\"room_id\": 16, \"from_user_id\": 16}');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL DEFAULT 1,
  `rider_id` int(11) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `status` enum('pending','confirmed','preparing','shipped','assigned_to_rider','picked_up','on_the_way','out_for_delivery','delivered','cancelled','refunded') DEFAULT 'pending',
  `shipping_address` text NOT NULL,
  `shipping_city` varchar(100) DEFAULT NULL,
  `shipping_province` varchar(100) DEFAULT NULL,
  `shipping_postal_code` varchar(20) DEFAULT NULL,
  `payment_method` enum('cash_on_delivery','credit_card','paypal','bank_transfer') DEFAULT 'cash_on_delivery',
  `payment_status` enum('pending','paid','failed','refunded') DEFAULT 'pending',
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `delivered_at` datetime DEFAULT NULL,
  `shipping_fee` decimal(10,2) DEFAULT 0.00,
  `shipping_provider` varchar(50) DEFAULT 'J&T Express',
  `tracking_number` varchar(100) DEFAULT NULL,
  `carrier` varchar(100) DEFAULT 'Standard Delivery',
  `estimated_delivery_date` date DEFAULT NULL,
  `product_total` decimal(10,2) DEFAULT 0.00,
  `delivery_fee` decimal(10,2) DEFAULT 0.00,
  `admin_commission` decimal(10,2) DEFAULT 0.00,
  `seller_earned` decimal(10,2) DEFAULT 0.00,
  `order_number` varchar(50) DEFAULT NULL,
  `billing_address` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `user_id`, `seller_id`, `rider_id`, `total_amount`, `status`, `shipping_address`, `shipping_city`, `shipping_province`, `shipping_postal_code`, `payment_method`, `payment_status`, `notes`, `created_at`, `updated_at`, `delivered_at`, `shipping_fee`, `shipping_provider`, `tracking_number`, `carrier`, `estimated_delivery_date`, `product_total`, `delivery_fee`, `admin_commission`, `seller_earned`, `order_number`, `billing_address`) VALUES
(29, 16, 1, 4, 555.00, 'cancelled', 'La Carlota, Philippines', NULL, NULL, NULL, '', 'pending', NULL, '2025-10-31 16:33:50', '2025-11-19 17:41:43', NULL, 55.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(33, 16, 1, 4, 463.00, 'cancelled', 'Rizal Laguna, Philippines', NULL, NULL, NULL, '', 'pending', 'please paki ingatan hehe', '2025-11-02 21:06:54', '2025-11-03 17:12:32', NULL, 55.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(36, 16, 1, 4, 191.00, 'delivered', 'None, La Carlota, Philippines', NULL, NULL, NULL, '', 'paid', NULL, '2025-11-03 16:07:02', '2025-11-10 23:46:25', NULL, 55.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(37, 16, 1, 4, 102.00, 'cancelled', 'None, La Carlota, Philippines', NULL, NULL, NULL, '', 'pending', NULL, '2025-11-03 16:25:24', '2025-11-19 17:41:35', NULL, 34.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(47, 16, 1, 4, 129.00, 'delivered', '43, Barangay Santo Niño, Tanay, Rizal, Philippines', NULL, NULL, NULL, '', 'paid', NULL, '2025-11-19 16:17:01', '2025-11-19 16:20:08', NULL, 43.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(48, 16, 1, 4, 3000.00, 'delivered', '43, Barangay Bagumbayan, Angono, Rizal, Philippines', NULL, NULL, NULL, '', 'paid', NULL, '2025-11-19 17:12:48', '2025-11-19 17:45:26', NULL, 1000.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(49, 16, 1, 4, 3696.00, 'delivered', '43, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, '', 'paid', NULL, '2025-11-20 15:05:13', '2025-11-24 11:31:25', NULL, 1232.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(50, 16, 1, 4, 180.00, 'delivered', '43, Oliveros Street, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, '', 'paid', NULL, '2025-11-21 18:21:05', '2025-11-24 19:28:22', NULL, 60.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(51, 16, 1, 4, 45.00, 'delivered', '43, Oliveros Street, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, '', 'paid', NULL, '2025-11-21 18:36:32', '2025-11-22 16:46:53', NULL, 15.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(52, 16, 1, 4, 162.00, 'delivered', '43, Haha Street, Barangay Bagumbayan (Pob.), Pililla, Rizal, Philippines', NULL, NULL, NULL, '', 'pending', NULL, '2025-11-24 07:34:31', '2025-11-26 01:36:19', NULL, 54.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(53, 16, 1, 4, 117.00, 'delivered', '12, Haha Street, Barangay San Isidro, Rodriguez, Rizal, Philippines', NULL, NULL, NULL, '', 'paid', NULL, '2025-11-24 11:08:30', '2025-11-24 19:50:42', NULL, 39.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 0.00, 0.00, 0.00, 0.00, NULL, NULL),
(60, 16, 1, NULL, 1045.00, 'cancelled', '43, Haha Street, Barangay Bagumbayan, Teresa, Rizal, Philippines', NULL, NULL, NULL, '', 'pending', '', '2025-11-25 00:45:27', '2025-11-25 08:49:39', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 995.00, 50.00, 49.75, 945.25, 'PF-20251125-E99ED70C', '43, Haha Street, Barangay Bagumbayan, Teresa, Rizal, Philippines'),
(62, 16, 1, NULL, 70.00, 'cancelled', '43, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-25 02:05:18', '2025-11-25 10:17:28', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 20.00, 50.00, 1.00, 19.00, 'PF-20251125-3BFE473C', '43, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines'),
(63, 16, 8, NULL, 194.00, 'cancelled', '43, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-25 02:18:12', '2025-11-26 01:37:00', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 144.00, 50.00, 7.20, 136.80, 'PF-20251125-7DD7EE06', '43, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines'),
(64, 16, 1, 4, 89.00, 'delivered', 'Barangay Bagumbayan, Angono, Rizal, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-25 16:00:44', '2025-11-26 01:37:56', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 39.00, 50.00, 1.95, 37.05, 'PF-20251126-A77287A7', 'Barangay Bagumbayan, Angono, Rizal, Philippines'),
(66, 25, 1, NULL, 122.00, 'cancelled', '24, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-26 05:05:59', '2025-11-26 13:21:09', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 72.00, 50.00, 3.60, 68.40, 'PF-20251126-615D4440', '24, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines'),
(69, 25, 1, NULL, 86.00, 'cancelled', '24, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-26 05:21:34', '2025-11-26 13:31:22', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 36.00, 50.00, 1.80, 34.20, 'PF-20251126-F9FCB517', '24, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines'),
(70, 25, 1, 26, 89.00, 'assigned_to_rider', '24, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-26 05:31:49', '2025-11-26 14:03:07', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 39.00, 50.00, 1.95, 37.05, 'PF-20251126-83888BF4', '24, Bagong Sikat, Barangay Poblacion, Cavinti, Laguna, Philippines'),
(71, 16, 1, NULL, 180.00, 'cancelled', '43, Haha Street, Barangay Bagumbayan, Angono, Rizal, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-26 21:25:59', '2025-11-27 22:37:14', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 130.00, 50.00, 6.50, 123.50, 'PF-20251127-17CEC559', '43, Haha Street, Barangay Bagumbayan, Angono, Rizal, Philippines'),
(72, 16, 1, 28, 82.00, 'picked_up', '43, Haha Street, Barangay Bagumbayan, Angono, Rizal, Philippines', NULL, NULL, NULL, 'cash_on_delivery', 'pending', '', '2025-11-27 14:02:25', '2025-11-27 22:14:07', NULL, 0.00, 'J&T Express', NULL, 'Standard Delivery', NULL, 32.00, 50.00, 1.60, 30.40, 'PF-20251128-C160D096', '43, Haha Street, Barangay Bagumbayan, Angono, Rizal, Philippines');

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL DEFAULT 1,
  `quantity` int(11) NOT NULL,
  `price_at_time` decimal(10,2) NOT NULL,
  `variant_id` int(11) DEFAULT NULL,
  `unit_price` decimal(10,2) DEFAULT NULL,
  `total_price` decimal(10,2) DEFAULT NULL,
  `status` enum('pending','confirmed','preparing','shipped','delivered','cancelled') DEFAULT 'pending',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`id`, `order_id`, `product_id`, `seller_id`, `quantity`, `price_at_time`, `variant_id`, `unit_price`, `total_price`, `status`, `created_at`) VALUES
(30, 29, 13, 1, 5, 100.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(34, 33, 20, 8, 12, 34.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(37, 36, 20, 8, 4, 34.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(38, 37, 20, 8, 2, 34.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(50, 47, 24, 8, 1, 56.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(51, 47, 25, 8, 1, 30.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(52, 48, 26, 8, 80, 25.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(53, 49, 24, 8, 44, 56.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(54, 50, 25, 8, 4, 30.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(55, 51, 25, 8, 1, 30.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(56, 52, 95, 8, 2, 39.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(57, 52, 25, 8, 1, 30.00, NULL, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(58, 53, 95, 8, 2, 39.00, 3, NULL, NULL, 'pending', '2025-11-25 16:44:28'),
(59, 60, 62, 8, 5, 0.00, NULL, 199.00, 995.00, 'pending', '2025-11-25 08:45:27'),
(61, 62, 83, 8, 1, 0.00, NULL, 20.00, 20.00, 'pending', '2025-11-25 10:05:18'),
(62, 63, 94, 8, 4, 0.00, NULL, 36.00, 144.00, 'pending', '2025-11-25 10:18:12'),
(63, 64, 95, 8, 1, 0.00, 5, 39.00, 39.00, 'pending', '2025-11-26 00:00:44'),
(65, 66, 94, 1, 2, 0.00, NULL, 36.00, 72.00, 'pending', '2025-11-26 13:05:59'),
(70, 69, 94, 1, 1, 0.00, NULL, 36.00, 36.00, 'pending', '2025-11-26 13:21:34'),
(71, 70, 91, 8, 1, 0.00, NULL, 39.00, 39.00, 'pending', '2025-11-26 13:31:49'),
(72, 71, 88, 8, 1, 0.00, NULL, 130.00, 130.00, 'pending', '2025-11-27 05:25:59'),
(73, 72, 84, 8, 1, 0.00, NULL, 32.00, 32.00, 'pending', '2025-11-27 22:02:25');

--
-- Triggers `order_items`
--
DELIMITER $$
CREATE TRIGGER `after_order_item_insert` AFTER INSERT ON `order_items` FOR EACH ROW BEGIN DECLARE prev_stock INT; SELECT stock_quantity INTO prev_stock FROM products WHERE id = NEW.product_id; INSERT INTO inventory_transactions ( product_id, transaction_type, quantity, previous_stock, new_stock, reference_type, reference_id ) VALUES ( NEW.product_id, 'sale', NEW.quantity, prev_stock, prev_stock - NEW.quantity, 'order', NEW.order_id ); IF (prev_stock - NEW.quantity) <= (SELECT low_stock_threshold FROM products WHERE id = NEW.product_id) THEN INSERT INTO low_stock_alerts (product_id, seller_id, threshold_quantity, current_stock) SELECT id, seller_id, low_stock_threshold, stock_quantity FROM products WHERE id = NEW.product_id ON DUPLICATE KEY UPDATE current_stock = VALUES(current_stock), alert_sent = FALSE; END IF; END
$$
DELIMITER ;



CREATE TABLE `order_tracking` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `status` varchar(50) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `tracking_number` varchar(100) DEFAULT NULL,
  `carrier` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `payout_requests` (
  `id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payout_method` varchar(50) NOT NULL,
  `notes` text DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `requested_at` datetime DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `paid_at` datetime DEFAULT NULL,
  `admin_notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `payout_requests`
--

INSERT INTO `payout_requests` (`id`, `rider_id`, `amount`, `payout_method`, `notes`, `status`, `requested_at`, `approved_at`, `paid_at`, `admin_notes`) VALUES
(1, 4, 20.00, 'gcash', NULL, 'paid', '2025-11-27 13:59:56', '2025-11-27 14:07:03', '2025-11-27 14:07:10', '');


CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock_quantity` int(11) DEFAULT 0,
  `image_url` varchar(255) DEFAULT NULL,
  `status` enum('active','inactive','out_of_stock','draft') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `sku` varchar(50) DEFAULT NULL,
  `weight` decimal(8,2) DEFAULT NULL,
  `dimensions` varchar(50) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `age_group` enum('puppy','adult','senior','all_ages') DEFAULT 'all_ages',
  `pet_type` enum('dog','cat','fish','bird','other') NOT NULL DEFAULT 'dog',
  `featured` tinyint(1) DEFAULT 0,
  `seller_latitude` decimal(10,8) DEFAULT 14.59950000,
  `seller_longitude` decimal(11,8) DEFAULT 120.98420000,
  `low_stock_threshold` int(11) DEFAULT 10,
  `is_low_stock` tinyint(1) GENERATED ALWAYS AS (`stock_quantity` <= `low_stock_threshold`) STORED,
  `meta_title` varchar(200) DEFAULT NULL,
  `meta_description` text DEFAULT NULL,
  `meta_keywords` varchar(255) DEFAULT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `sale_price` decimal(10,2) DEFAULT NULL,
  `sale_start_date` datetime DEFAULT NULL,
  `sale_end_date` datetime DEFAULT NULL,
  `cost_price` decimal(10,2) DEFAULT NULL COMMENT 'Cost/purchase price for valuation'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO `products` (`id`, `seller_id`, `category_id`, `name`, `description`, `price`, `stock_quantity`, `image_url`, `status`, `created_at`, `updated_at`, `sku`, `weight`, `dimensions`, `brand`, `age_group`, `pet_type`, `featured`, `seller_latitude`, `seller_longitude`, `low_stock_threshold`, `meta_title`, `meta_description`, `meta_keywords`, `slug`, `sale_price`, `sale_start_date`, `sale_end_date`, `cost_price`) VALUES
(19, 8, 2, 'Cat Feather Teaser Toy Pet spring Bell Feather Stick Rod Funny Interactive Toy', 'Bring endless fun and excitement to your cat’s playtime with the Cat Feather Teaser Toy! Designed to awaken your cat’s natural hunting instincts, this interactive toy features colorful feathers, a springy rod, and a tiny bell that jingles with every move — guaranteed to keep your feline entertained for hours.', 100.00, 47, '/static/uploads/products/1e7ab217ca034cfea40e2b0f3fb5488a_4065271d09612558a2589304cbe9bf75.jpg', 'active', '2025-10-26 19:18:00', '2025-11-26 13:21:06', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(20, 8, 2, 'Adjustable Nylon Pet Leash Dog Leash Cat Puppy Leash Kitty Leash For Dog Leash accessories Supplies', 'Keep your furry friend safe and stylish with our Adjustable Nylon Pet Leash — perfect for cats, puppies, and small dogs! Made from durable, high-quality nylon, this leash offers both comfort and control during walks, training, or outdoor adventures.', 34.00, 52, '/static/uploads/products/3f60ac94f4324809b15a5896c86ce658_BLACK.jpg', 'active', '2025-10-26 19:20:02', '2025-11-26 13:21:06', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'adjustable-nylon-pet-leash-dog-leash-cat-puppy-leash-kitty-leash-for-dog-leash-accessories-supplies', NULL, NULL, NULL, NULL),
(23, 8, 2, 'Cat laser funny stick cat teaser pointer red laser point 2 in 1 modes pointer', 'Unleash the fun! This cat laser funny stick offers two exciting modes to keep your kitty engaged. The bright red laser point provides endless chasing action, satisfying their natural hunting instincts. Get ready for hours of interactive play!', 45.00, 97, '/static/uploads/products/8c6a263b946a4a9b9bbea5887a47d818_RED_1.jpg', 'active', '2025-11-04 04:42:38', '2025-11-13 15:26:50', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 8, 2, 'Cat mouse toy chasing toy plush mouse in cage pet interactive cat toy supplies', 'Tap into your cat\'s natural hunting instincts with this exciting plush mouse in a cage toy! The sturdy, round cage allows the mouse to roll and wobble erratically, mimicking real prey your cat can safely bat, chase, and pounce on. Perfect for solo play and essential exercise!', 56.00, 0, '/static/uploads/products/48ad3e2085d54762b93985de85e10737_debe07ce01e51a77c18cbcc68a695caa.jpg', 'active', '2025-11-04 04:47:57', '2025-11-20 15:05:13', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(25, 8, 2, 'Cat Scratches kitten Scratching Cardboard High-density Corrugated paper Board', 'Give your cat the perfect scratching surface! This board\'s unique corrugated texture mimics natural tree bark, encouraging healthy claw maintenance, stretching, and territory marking. The high-density design stands up to even the most vigorous scratching sessions. It\'s more than a scratcher—it\'s a vital tool for your cat\'s physical and mental well-being.', 30.00, 112, '/static/uploads/products/9f2bae9c6d85418091c98bfd7e5d0a7c_sg-11134201-22110-hl6kvf1jvdkv1a.jpg', 'active', '2025-11-04 04:50:39', '2025-11-24 07:34:31', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(26, 8, 2, 'Pet Collar Dog Collar Cat Paw Collar With Bell Safety Buckle Neck for Puppy and Kitty Accessories', 'Give your kitty or puppy both style and safety! This charming collar features a sweet cat paw design and is equipped with a vital safety/breakaway buckle—designed to release under pressure, preventing choking if the collar gets snagged. The attached bell alerts wildlife (and you!) to their whereabouts. Comfortable, adjustable, and cute!', 25.00, 0, '/static/uploads/products/03430c2bc84e4e799451a371bc390180_47b754e5bb29a18c7d2e1b83e610e831.jpg', 'active', '2025-11-04 04:53:52', '2025-11-19 17:12:48', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(30, 8, 1, 'PEDIGREE Tasty Bites Chewy Cubes Treats for Dogs 50g (6-Pack)', 'Give your dog a tasty and nutritious meal with PEDIGREE Wet Food. Each 80g pack is made with real meat and essential nutrients that help support your dog’s overall health. It’s soft, flavorful, and easy to mix with dry kibble—perfect for picky eaters or dogs who prefer moist meals.', 505.00, 64, '/static/uploads/products/04ccf1f632204624a0fe84852628d928_0ea1b6cb-f834-49e1-ad3e-250387993a6b.jpg', 'active', '2025-11-23 23:19:51', '2025-11-23 23:19:51', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-tasty-bites-chewy-cubes-treats-for-dogs-50g-6-pack', NULL, NULL, NULL, NULL),
(31, 8, 1, 'PEDIGREE NutriDefense Puppy Dog Food - Dry Puppy Food 1.3kg', 'Give your growing puppy the right start with PEDIGREE NutriDefense. Specially formulated for young dogs, this dry food provides complete and balanced nutrition to support healthy growth, strong immunity, and proper development.', 582.00, 27, '/static/uploads/products/1dd2b6f8104d454fa0a0d72dbd488536_ce5163d7-9205-471d-95a7-1203c4036aea.jpg', 'active', '2025-11-23 23:24:05', '2025-11-23 23:24:05', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-nutridefense-puppy-dog-food-dry-puppy-food-1-3kg', NULL, NULL, NULL, NULL),
(32, 8, 1, 'PEDIGREE Dry Adult Dog Food – Beef & Vegetable Flavour, 1.5kg (6-pack)', 'Give your dog a healthy and satisfying meal with PEDIGREE Dry Adult Dog Food. Specially made for adult dogs, this kibble provides complete and balanced nutrition to support strong muscles, good digestion, and overall daily energy.\r\n\r\nEach pack contains quality protein, essential vitamins, minerals, and antioxidants to promote a strong immune system and long-term health. The crunchy kibble texture also helps reduce tartar build-up, supporting better oral hygiene.\r\n\r\nThis convenient 6-pack of 1.5kg bags is perfect for daily feeding, stocking up at home, or ensuring your dog always enjoys a fresh and nutritious meal—no matter the flavor you choose.', 299.00, 57, '/static/uploads/products/c7b3d42b9df04954bc3af981426a0c44_a653e3d4-a366-4fc2-bf5f-0efd52f2f446.jpg', 'active', '2025-11-23 23:26:13', '2025-11-23 23:27:35', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-dry-adult-dog-food-beef-vegetable-flavour-1-5kg-6-pack', NULL, NULL, NULL, NULL),
(33, 8, 1, 'PEDIGREE Dry Dog Food for Adult 3kg', 'PEDIGREE Dry Dog Food provides complete and balanced nutrition specially made for adult dogs. Formulated with quality protein, essential vitamins, and minerals, it helps support strong muscles, healthy digestion, and overall vitality. The crunchy kibble texture also helps maintain oral hygiene by reducing tartar build-up.\r\n\r\nPerfect for daily feeding, this 3kg pack offers a satisfying and nutritious meal that adult dogs of all breeds will enjoy—available in different flavors depending on your dog’s preference.', 541.00, 14, '/static/uploads/products/1387886d9fe94c369653f49f0fd149fe_c5d3e885-dfa5-49f2-928d-8d45f9d13115.jpg', 'active', '2025-11-23 23:29:01', '2025-11-23 23:29:01', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-dry-dog-food-for-adult-3kg', NULL, NULL, NULL, NULL),
(34, 8, 1, 'CESAR Naturally Crafted Premium Dog Wet Food 85g (6-Pack)', 'Treat your dog to a delicious and nutritious meal with CESAR Naturally Crafted Premium Dog Wet Food. Made with high-quality ingredients and crafted with care, each 85g pack delivers a soft, flavorful texture that dogs love.\r\n\r\nEnriched with essential nutrients, vitamins, and minerals, it supports your dog’s overall health, including strong muscles, a healthy coat, and good digestion. Perfect as a complete meal or a tasty complement to dry food, this 6-pack ensures your dog always has a fresh and satisfying meal ready.', 445.00, 15, '/static/uploads/products/64caf4473cfa45f18624da8b1633fabb_e449285a-5108-4f72-bb80-1ed9be0448f6.jpg', 'active', '2025-11-23 23:30:45', '2025-11-23 23:30:45', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'cesar-naturally-crafted-premium-dog-wet-food-85g-6-pack', NULL, NULL, NULL, NULL),
(35, 8, 1, 'Cesar Premium Dog Wet Food 100g (3-Pack)', 'Give your dog a tasty and nutritious meal with Cesar Premium Dog Wet Food. Each 100g pack is made with high-quality ingredients and crafted to deliver a soft, flavorful texture that dogs love.\r\n\r\nEnriched with essential nutrients, vitamins, and minerals, it helps support your dog’s overall health, including strong muscles, a healthy coat, and proper digestion. Perfect as a complete meal or as a delicious complement to dry food, this 3-pack ensures your dog always enjoys a fresh and satisfying meal.', 223.00, 47, '/static/uploads/products/568e10f8ea144b938c6fbddaefe13b2e_e449285a-5108-4f72-bb80-1ed9be0448f6.jpg', 'active', '2025-11-23 23:31:55', '2025-11-23 23:31:55', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'cesar-premium-dog-wet-food-100g-3-pack', NULL, NULL, NULL, NULL),
(36, 8, 1, 'PEDIGREE Tasty Bites Chewy Cubes Treats for Dogs 50g (6-Pack)', 'Reward your dog with PEDIGREE Tasty Bites Chewy Cubes, a delicious and wholesome treat they’ll love. Each 50g pack is made with high-quality ingredients and a soft, chewy texture that’s perfect for training, rewarding good behavior, or simply showing some love.\r\n\r\nEnriched with essential nutrients, these treats support overall health while keeping your dog happy and engaged. This convenient 6-pack ensures you always have tasty bites ready for your furry friend.', 617.00, 67, '/static/uploads/products/946c50d20d494dd7b030dfc8acdafc80_a9f704e5-5107-48a6-9b9d-6891243a230d.jpg', 'active', '2025-11-23 23:33:29', '2025-11-23 23:33:29', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-tasty-bites-chewy-cubes-treats-for-dogs-50g-6-pack-1', NULL, NULL, NULL, NULL),
(37, 8, 1, 'CESAR Dog Food Wet Pouch for Adult Dog 70g (6-Pack)', 'Treat your adult dog to a delicious and nutritious meal with CESAR Wet Food Pouches. Each 70g pouch is crafted with high-quality ingredients to deliver a soft, flavorful texture that dogs love.\r\n\r\nPacked with essential nutrients, vitamins, and minerals, it supports overall health, including strong muscles, a shiny coat, and good digestion. Perfect as a complete meal or a tasty complement to dry food, this 6-pack ensures your dog always enjoys a fresh and satisfying meal.', 248.00, 53, '/static/uploads/products/29c173aabd1247128faf5e11f08950b9_3e44fef2-b3be-4a6c-9732-55ee02e8c912.jpg', 'active', '2025-11-23 23:35:50', '2025-11-23 23:35:50', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'cesar-dog-food-wet-pouch-for-adult-dog-70g-6-pack', NULL, NULL, NULL, NULL),
(38, 8, 1, 'PEDIGREE Multipack Wet Dog Food  for Adult with Chicken in Gravy 130g (12-Pack)', 'Treat your adult dog to a tasty and wholesome meal with PEDIGREE Wet Dog Food. Each 130g pouch contains succulent chicken in rich gravy, packed with essential nutrients, vitamins, and minerals to help maintain strong muscles, a healthy coat, and overall wellbeing.\r\n\r\nThis 12-pack provides a convenient supply of fresh, flavorful meals, perfect as a complete dish or a delicious addition to dry food for everyday feeding.', 303.00, 62, '/static/uploads/products/3bd59f0cd861468c902c0e027b844d26_b56d45f1-5d93-4e51-900f-d8319a8ea8df.jpg', 'active', '2025-11-23 23:37:43', '2025-11-23 23:37:43', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-multipack-wet-dog-food-for-adult-with-chicken-in-gravy-130g-12-pack', NULL, NULL, NULL, NULL),
(39, 8, 1, 'PEDIGREE Adult Dog Food in Beef & Vegetable Flavor 20kg', 'Provide your adult dog with complete and balanced nutrition with PEDIGREE Adult Dog Food. Made with quality protein, vitamins, and minerals, it supports strong muscles, healthy digestion, and overall vitality.\r\n\r\nThe delicious beef and vegetable flavor keeps mealtime enjoyable, while the crunchy kibble helps maintain oral health by reducing tartar buildup. This large 20kg pack is ideal for households with one or more adult dogs, ensuring a consistent supply of nutritious meals.', 2852.00, 89, '/static/uploads/products/d04f4520ba21482a8f44e257b5a448b2_783c20c5-a8fc-4adb-9562-acea1c9d7667.jpg', 'active', '2025-11-23 23:39:26', '2025-11-23 23:39:26', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-adult-dog-food-in-beef-vegetable-flavor-20kg', NULL, NULL, NULL, NULL),
(40, 8, 1, 'PEDIGREE Wet Dog Food Can 400g (2-Pack)', 'Treat your dog to a wholesome and tasty meal with PEDIGREE Wet Dog Food. Each 400g can is made with high-quality ingredients to provide complete and balanced nutrition, supporting strong muscles, healthy digestion, and overall wellbeing.\r\n\r\nThe soft, flavorful texture makes it perfect as a standalone meal or as a complement to dry food. This convenient 2-pack ensures your dog always has a fresh and satisfying meal ready.', 236.00, 71, '/static/uploads/products/028c4cfa80724871a4917dac419e079c_b782ee43-9929-4e86-a27a-7386b4397b3c.jpg', 'active', '2025-11-23 23:42:44', '2025-11-23 23:42:44', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-wet-dog-food-can-400g-2-pack', NULL, NULL, NULL, NULL),
(41, 8, 1, 'PEDIGREE Multipack Wet Dog Food  for Adult with Chicken in Gravy 130g (12-Pack)', 'Delicious & Nutritious Meal for Your Dog! 🐶\r\n\r\n\r\n\r\nPEDIGREE Wet Dog Food is the perfect choice for your adult dog\'s daily diet. Each 130g pouch is filled with simmered beef and veggies, ensuring a balanced meal packed with essential nutrients.\r\n\r\n\r\n\r\nWhy Choose PEDIGREE?\r\n\r\n- High-Quality Protein: Supports strong muscles for your active pet.\r\n\r\n- Omega 6 & Zinc: Promotes healthy skin and a shiny coat.\r\n\r\n- Calcium & Phosphorus: Essential for strong bones and teeth.\r\n\r\n\r\n\r\nConvenient Packaging\r\n\r\nAvailable in a handy 12-pack, this wet dog food makes feeding time easy and enjoyable for both you and your furry friend.\r\n\r\n\r\n\r\nProduct Variation\r\n\r\nEnjoy the PEDIGREE Simmered Beef with Vegetables in a new loaf packaging, ensuring freshness and taste in every bite. Each pack contains 12 pouches of 130g each.\r\n\r\n\r\n\r\nGive your dog the tasty and wholesome meal they deserve every day with PEDIGREE Wet Dog Food! 🐾\r\n\r\nProduct Ratings', 444.00, 34, '/static/uploads/products/16c20171ad524bbab758f0be8416d19a_9378d48a-5bc1-47eb-96f2-394cce6b1588.jpg', 'active', '2025-11-23 23:49:36', '2025-11-23 23:49:36', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-multipack-wet-dog-food-for-adult-with-chicken-in-gravy-130g-12-pack-1', NULL, NULL, NULL, NULL),
(42, 8, 1, 'PEDIGREE Dog Dry Food Mini Small Breed in Beef Lamb Vegetable Flavor 2.7kg', '🐶Delicious Flavor: Satiate your dog\'s taste buds with a delicious blend of beef, lamb, and vegetable flavors they\'ll love 🐶Specially Formulated for Small Dogs: This dog food is perfectly designed to cater to the unique nutritional needs of small breed dogs aged 9+ months 🐶Digestive Support: Our dog food recipe includes dietary fiber to help support a healthy digestive system 🐶Shiny Coat in 6 Weeks: Omega 6 and zinc in our PEDIGREE dry dog food nourishes your dog\'s skin and ensures a shiny coat 🐶Effective Body System: PEDIGREE MINI dog food is packed with vitamins and minerals to keep your dog\'s body functioning optimally 🐶Strong Bones & Teeth: Our adult dog food contains a blend of calcium and phosphorus that work together to promote strong bones and teeth 🐶Muscle Strength: High-quality protein in our formula helps build and maintain strong muscles PEDIGREE MINI dog food (2.7 kg) is expertly crafted for small dogs aged 9+ months, offering a nutritious and delicious meal that brings excitement to their mealtimes. Our beef, lamb, and vegetable flavored dog food provides a tantalizing blend that your little furry friend won\'t be able to resist. Experience the five signs of good health with our specially formulated recipe: 🛡️Boosted Immunity: Essential vitamins and minerals work together to support your dog\'s immune system. 🌾Supported Digestion: Dietary fiber in our recipe helps maintain a healthy digestive system. 🌟Healthy Coat: Omega 6 and zinc nourish the skin and ensure a shiny coat within six weeks. 💪Enhanced Muscle Strength: High-quality protein in our formula supports strong muscles. 🦴Strengthened Bones & Teeth: Calcium and phosphorus work together to promote strong bones and teeth. 🛍️High-Quality Ingredients🛍️ • Cereal (corn, wheat) • Poultry and poultry by products • Soybean products (soy bean meal, full fat soy bean) • Oils (chicken, palm) • Flavors • Hydrolyzed feather meal • Wheat flour • Minerals • Corn gluten meal • Vitamins • Iodized salt • Methionine • Food coloring • Preservatives • Dried vegetables 📊Nutritional Analysis📊 • Crude protein (min) - 21.0% • Crude fat (min) - 12.0% • Crude fiber (max) - 5.0% • Moisture (max) - 12.0% 🍽️Feeding Recommendation🍽️ Rest assured with our nutritious recipe that contains: • 1-5 kg dog: 25-84g dog food daily • 5-7 kg dog: 84-108g dog food daily • 7-10 kg dog: 108-141g dog food daily 📦What\'s Inside the Package📦 • 1 x 2.7 kg bag of PEDIGREE MINI Dog Food for Small Breed Dogs - Beef, Lamb & Veggie Flavor Order now and give your dog a delicious and nutritious meal that they will love! PEDIGREE - Nourishing Dogs for a Lifetime of Love.', 464.55, 56, '/static/uploads/products/35fb399f0f87460a9a3e9c9f8a6516a2_2bd6fba8-c13b-4081-a60d-035c320a4ab1.jpg', 'active', '2025-11-23 23:51:42', '2025-11-23 23:51:42', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-dog-dry-food-mini-small-breed-in-beef-lamb-vegetable-flavor-2-7kg', NULL, NULL, NULL, NULL),
(43, 8, 1, 'Pedigree Dentastix Treats for Puppy 56g (3-Pack)', 'At Pedigree, everything we do is for the love of dogs. Pedigree Pouch does not only provide your dogs with Complete and Balanced nutrition, but also gives them a superb taste with meaty chunks for their enjoyment. Ideal meal for dogs of all breeds and sizes, from Pugs to Labradors Tempting aroma and flavour effective to attract fussy eaters', 250.32, 75, '/static/uploads/products/7e4fd25c1bc14d8b98670d117060e064_cb5ff617-9703-41e2-b041-aa5ce7f10a22.jpg', 'active', '2025-11-23 23:54:08', '2025-11-23 23:54:08', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-dentastix-treats-for-puppy-56g-3-pack', NULL, NULL, NULL, NULL),
(44, 8, 1, 'PEDIGREE DentaStix Dog Treats for Adult Small Breed Dogs Weekly Pack 110g (3-Pack)', '•Special X-Shape Design: PEDIGREE Dentastix dog snacks boast an innovative x-shape design that provides gentle, abrasive cleaning action for your dog\'s teeth•Tailored For All Dog Sizes: These PEDIGREE dog dental sticks are thoughtfully designed to accommodate the oral structures of puppies and small, medium, and large dogs alike•Triple Action Advantage: PEDIGREE dog treats deliver a triple action benefit, aiding in the reduction of tartar accumulation, cleaning hard-to-reach teeth, and promoting gum health•Significant Tartar Reduction: These dental treats for dogs can help reduce tartar buildup on your dog\'s teeth by up to 80%•Abrasive, Chewy Texture: Dentastix dog snacks feature an abrasive, chewy texture that stimulates saliva flow to help wash away debris from your dog\'s teeth•Healthy Gum Support: PEDIGREE Dentastix dog snacks contribute to your dog\'s overall gum health, keeping them strong and resilient•Powerful Active Ingredients: These dog snacks contain active ingredients like zinc sulphate and sodium tripolyphosphate, which work to bind calcium in saliva and slow down tartar accumulation with just one stick per day•Healthy Bones: PEDIGREE Dentastix dog treats are enriched with calcium, an essential nutrient for maintaining your dog\'s strong, healthy bones•Low-Fat, No Added Sugar: These pet treats are a wholesome, low-fat option without added sugar, ensuring your dog stays both happy and healthyPEDIGREE Dentastix Dog Snacks are expertly crafted to give your dog the ultimate dental care experience. With a unique X-shape and an irresistibly abrasive, chewy texture, these treats work to clean those hard-to-reach teeth while supporting gum health. The triple-action formula of PEDIGREE Dentastix reduces tartar build-up, ensuring your best friend\'s smile stays bright and healthy.Our Dentastix dog treats contain active ingredients like zinc sulphate and STPP for enhanced dental protection. High in calcium and low in fat, these treats are perfect for maintaining your dog\'s overall health. Plus, with no added sugar, you can feel good about giving your pup a tasty and beneficial treat.🐟High-Quality Ingredients🍗•Wheat starch•Flours (wheat, maize)•Glycerine•Maize gluten•Gum•Poultry liver•Sodium tripolyphosphate•Calcium carbonate•Gelatin•Potassium chloride•Preservative•Flavors•Zinc sulphate📊Guaranteed Analysis📊At PEDIGREE, we ensure the quality of our treats through a thorough analysis of the nutrients they provide. Our Dentastix dog snacks guarantee the following:•Protein (min) – 8%•Fat (min) – 1%•Fiber (max) – 1%•Moisture (max) – 18%📅Daily Meal Recommendation📅To maintain optimal dental health, we recommend the following feeding guidelines for your dog, Please refer the packgage for the information📦Inside the Package📦• Each purchase comes with PEDIGREE DentaStix Dog Treats for Adult Small Breed Dogs Weekly Pack 110g (3-Pack),Your dog\'s dental health is essential, and PEDIGREE Dentastix Dog Snacks make it easy to prioritize their oral hygiene. With their unique shape, powerful cleaning action, and irresistible taste, these treats are more than just a snack – they\'re a smart way to support your dog\'s oral care. Treat your dog to PEDIGREE Dentastix today and let them enjoy a happy, healthy smile!', 444.00, 324, '/static/uploads/products/b380f10dd5e04f6d8620dc33d22a6b94_cb5ff617-9703-41e2-b041-aa5ce7f10a22.jpg', 'active', '2025-11-23 23:55:44', '2025-11-23 23:55:44', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-dentastix-dog-treats-for-adult-small-breed-dogs-weekly-pack-110g-3-pack', NULL, NULL, NULL, NULL),
(45, 8, 1, 'PEDIGREE Good Chew Dog Treats for Small Dogs in Beef Flavor 53g (3-Pack)', 'Good Bye Bad Chew, PEDIGREE Good Chew Dog Treat 🍗High-Quality Ingredients🍗 • Maize Strach • Beef Collagen • Glycerine • Poultry Liver • Mineral • Preservatives • Food Colouring • Flavor 📊Guaranteed Analysis📊 At PEDIGREE, we ensure the quality of our treats through a thorough analysis of the nutrients they provide. • Protein (min) – 25% • Fat (min) – 0.8% • Fiber (max) – 1% • Moisture (max) – 22% 🍽️Feeding Recommendation🍽️ To maintain optimal dental health, we recommend the following feeding guidelines, please refer to the package for the information 📦Inside the Package📦 • Each purchase comes with PEDIGREE Good Chew Dog Treats for Small Dogs in Beef Flavor 53g,Order now and give your dog a delicious and nutritious treat that they will love! PEDIGREE - Nourishing Dogs for a Lifetime of Love.', 444.00, 84, '/static/uploads/products/ad2a037607b5434881a96bf2b96c07aa_2c0ceba8-ce1a-4672-8640-b09d8dc43d86.jpg', 'active', '2025-11-23 23:57:39', '2025-11-23 23:57:39', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-good-chew-dog-treats-for-small-dogs-in-beef-flavor-53g-3-pack', NULL, NULL, NULL, NULL),
(46, 8, 1, 'PEDIGREE Dentastix Chewy Chunx Dog Treats in Smoky Chicken Flavor 68g (3-Pack)', '• VETERINARIAN-DEVELOPED RECIPES - This PEDIGREE Dentastix Chewy Chunx Dog Dental Treat recipe is developed with veterinarians, so you can be sure that your dog is getting the best possible nutrition • SMOKY CHICKEN FLAVOR - Your dog will love the taste of these PEDIGREE Treats for Dog, which come in a Smoky Chicken Flavor • HELPS CLEAN TEETH - With PEDIGREE Dog Snacks, you can enjoy the delicious taste of a mouth-watering treat with cleaning power to keep your dog\'s pearly whites clean and healthy • SUPPORTS GUM HEALTH - The PEDIGREE Dog Treats are a tasty and safe way to help your dog maintain their gum health LOW IN FAT FOR A HEALTHY DOG - These PEDIGREE Dentastix Chewy Chunx Dog Treats have less than 2% fat, making them a healthy Treats for Dog🍗High-Quality Ingredients🍗•Flour (Wheat, Maize) •Wheat Strach •Glycerine •Maize Gluten •Gum •Poultry Liver •Sodium Tripolyphosphate •Calcium Carbonate•Gelatin•Potassium Chloride •Preservative•Flavour•Zinc Sulphate📊Guaranteed Analysis📊At PEDIGREE, we ensure the quality of our treats through a thorough analysis of the nutrients they provide. •Protein (min) – 8%•Fat (min) – 1%•Fiber (max) – 1%•Moisture (max) – 18%🍽️Feeding Recommendation🍽️To maintain optimal dental health, we recommend the following feeding guidelines for your dogSmall Breed 5-10kg  : 4pc/DayMedium  Breed 10-25kg  : 5 pc/Day📦Inside the Package📦• Each purchase comes with PEDIGREE Dentastix Chewy Chunx Dog Treats in Smoky Chicken Flavor 68g (3-Pack),Order now and give your dog a delicious and nutritious treat that they will love! PEDIGREE - Nourishing Dogs for a Lifetime of Love.', 444.00, 52, '/static/uploads/products/be1221855e5447a6ac340bd42d361d8b_937a83b1-45e8-4a82-9d08-48d8f8c1b412.jpg', 'active', '2025-11-23 23:59:23', '2025-11-23 23:59:23', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-dentastix-chewy-chunx-dog-treats-in-smoky-chicken-flavor-68g-3-pack', NULL, NULL, NULL, NULL),
(47, 8, 1, 'PEDIGREE Schmackos STRAP Meat Jerky Dog Treats 70g (3-Pack)', '•🐶 OMEGA 6: Spoil your dog with delicious, smoky-flavored treats packed with omega 6, excellent for their heart health.•🐶 LOW FAT: Packed with high-quality protein and low fat, our dog food is formulated to enhance the optimal health and well-being of your furry companion.•🐶 Soft Texture: Dog treats with a combination of deliciousness and a soft, chewy texture from real meat.•🐶 Two Variants: PEDIGREE® SCHMACKOS™ comes in 2 variants, STIX and STRAP, to suit your pet\'s preferences.•🐶 Share Moments of Happiness: Strengthen the bond with your pet. Share unforgettable moments of happiness with PEDIGREE® SCHMACKOS™.PEDIGREE® SCHMACKOS™ introduces a new recipe from PEDIGREE® Meat Jerky! With added benefits such as Omega 6, Vitamin E, High Protein, and Low Fat, PEDIGREE® SCHMACKOS™ dog treats contain 100% Complete and Balanced Nutrition.Treat your dog to PEDIGREE® SCHMACKOS™ Smoky Beef Flavour, either as a reward or as a supplement to their daily nutrition. These dog treats are a perfect combination of deliciousness and a soft, chewy texture, making them the perfect daily treat for your furry friend. Made with omega 6 and low-fat content, you no longer have to worry about the risk of being overweight in your beloved dog.As a pet food and treat brand supported by the WALTHAM Global Pet Nutrition Institute, PEDIGREE® ensures its products contain the best nutrients. With a variety of flavors and textures, your dog will never get bored with these delicious treats.🌽High-Quality Ingredients 🌽● Starch (tapioca and/or wheat)● Gluten (wheat and/or corn)● Glycerin● Poultry liver● Sugar● Minerals● Vegetable oil● Flavour● Preservatives● Colour● Vitamins📊Quality Assurance 📊PEDIGREE® SCHMACKOS™ is formulated to meet your dog\'s nutritional needs. Here\'s the guaranteed analysis of the product:Crude Protein (min.) = 28.0%Crude Fat (min.) = 4.0%Crude Fiber (max.) = 2.0%Moisture (max.) = 20.0%Calcium (max.) = 1.2%Total Phosphorus (max.) = 0.8%🍴Feeding Recommendation 🍴You can give PEDIGREE® SCHMACKOS™ to dogs over 3 months old. Follow these feeding recommendations based on your dog\'s size:• Toy Breed Dogs (3-5kg): 0.5-1 piece/day• Small Dogs (5-10kg): 1-1.5 pieces/day• Medium Dogs (10-25kg): 1.5-3 piece/day• Large Dogs (25-50kg): 3-5 piece/day📦In the Package 📦• Each purchase comes with PEDIGREE Schmackos Meat Jerky Dog Treats Smoky Beef Flavor 70g (3-Pack),PEDIGREE® SCHMACKOS™ dog treats are more than just snacks – they\'re a way to create everlasting memories and strengthen the bond between you and your furry friend. Spoil your dog with delicious and nutritious treats from PEDIGREE®.', 444.00, 76, '/static/uploads/products/0c74c9559e6c4b9e992191087cb80763_518f3f6b-bd0c-4b88-8f7e-880742347d35.jpg', 'active', '2025-11-24 00:00:43', '2025-11-24 00:00:43', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pedigree-schmackos-strap-meat-jerky-dog-treats-70g-3-pack', NULL, NULL, NULL, NULL),
(48, 8, 2, 'Extra Large Cat Litter Box Open Top high Sided Litter Box Portable Anti Splashing Durable', 'An extra-large open top litter box with high sides is designed for maximum space and containment, making it ideal for bigger cats, multiple cats, or very messy diggers. The high walls help prevent litter from being kicked out or urine from splashing, reducing mess on the floor. Despite the tall sides, the open-top design provides easy access for the cat, making it comfortable for entering, exiting, and digging.\r\n\r\nThe box is made from durable materials — often high-impact plastic or stainless steel — so it can withstand regular use, scratching, and the weight of litter. Durable plastics are typically BPA-free and resistant to cracking, while stainless steel versions are rust-resistant, non-porous (which helps prevent odor buildup), and very easy to clean. For cleaning, the smooth interior surface (plastic or metal) makes scooping and rinsing simple.\r\n\r\nTo make it more portable, some models include handles on the sides, so you can carry it when disposing litter or moving the box. The high wall design also helps with anti-splash, keeping waste and litter inside, which contributes to better hygiene.\r\n\r\nAdditionally, many of these litter boxes are spacious enough for large cats to turn around comfortably, giving them a sense of space and privacy.', 150.00, 32, '/static/uploads/products/b4faba4cd52746529319a920a8eccaee_56ea41c1-fdbe-4a43-9f38-3aaf24671857.jpg', 'active', '2025-11-24 00:09:15', '2025-11-24 00:09:15', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'extra-large-cat-litter-box-open-top-high-sided-litter-box-portable-anti-splashing-durable', NULL, NULL, NULL, NULL),
(49, 8, 2, 'Cat Litter Mat with Double-Layer Honeycomb Design for Superior Litter Trapping', 'Cat Litter Mat (Double‑Layer Honeycomb) is a smart, effective mat designed to catch stray litter and protect your floor, while staying gentle on your cat’s paws. It consists of two layers made from high‑quality EVA foam: the top honeycomb layer and a waterproof base layer.', 109.00, 323, '/static/uploads/products/59d8afd6fd2a4922a7f867e43159e919_336a2c0e-9537-4c61-af47-aa203156a993.jpg', 'active', '2025-11-24 00:11:01', '2025-11-24 00:11:01', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'cat-litter-mat-with-double-layer-honeycomb-design-for-superior-litter-trapping', NULL, NULL, NULL, NULL),
(50, 8, 2, 'Cat Litter - (10Liter)', 'Brand: Purreetty Prite\r\n\r\nType: Clumping Cat Litter\r\n\r\nMaterial: Natural Bentonite Clay\r\n\r\nVolume: 10 Liters\r\n\r\nTexture: Fine sand-like granules\r\n\r\nClumping: Fast and firm clumping\r\n\r\n\r\n\r\nQuestions and Concerns:\r\n\r\n\r\n\r\nQ: Is this cat litter safe for kittens?\r\n\r\nA: Yes, Purreetty Prite Bentonite Cat Litter is safe and gentle for kittens, adults, and senior cats.\r\n\r\n\r\n\r\nQ: How effective is the odor control?\r\n\r\nA: The bentonite clay absorbs moisture quickly and neutralizes odors to keep your home smelling fresh.\r\n\r\n\r\n\r\nQ: Does this litter create dust?\r\n\r\nA: This litter is formulated to be low dust, reducing mess and improving air quality.\r\n\r\n\r\n\r\nQ: Will my cat track the litter outside the box?\r\n\r\nA: The fine sand-like texture helps minimize tracking, but some litter may still cling to your cat’s paws.\r\n\r\n\r\n\r\n📌Please note that slight color variations and measurement discrepancies may occur.\r\n\r\n\r\n\r\n🌟We value your feedback, so please contact us before leaving negative comments. \r\n\r\n\r\n\r\n✅Resellers are welcome, and for bulk orders or inquiries, kindly send us a private message.', 235.00, 1324, '/static/uploads/products/236e7981b88945fd9afd6cad9b449957_19c4378a-d32f-48d8-9ed5-446729b0156d.jpg', 'active', '2025-11-24 00:12:49', '2025-11-24 00:12:49', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'cat-litter-10liter', NULL, NULL, NULL, NULL),
(51, 8, 2, 'True Test Cat litter (5L & 10L)', 'True Test Bentonite Cat liter\r\n\r\nUltra Absorbent\r\n\r\nAvailable in 24 flavors - Lemon, Coffee, Apple & Lavender\r\n\r\nAvailable in 2 sizes - 5LITER and 10 LITER', 205.00, 75, '/static/uploads/products/acd388901c784a49a58a10b53e94e917_4092b0a6-028f-4d4f-a5a7-3d599b07c6cb.jpg', 'active', '2025-11-24 00:18:13', '2025-11-24 00:18:13', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'true-test-cat-litter-5l-10l', NULL, NULL, NULL, NULL),
(52, 8, 2, 'CATSAN Ultra Odor Cat Litter Sand for Cats of All Ages 10L', '• 100% Hygiene Protection: CATSAN®cat litter is designed to provide your home with hygiene protection.• Absorb Odor: This cat litter sand is designed to prevent odor before it can develop.• Low-dust, Unscented: Formulated to minimize dust and is completely unscented for a clean, natural experience.• Made from Sodium Bentonite: The highly absorbent hygiene cat litter sand consists of unique mineral granules with guaranteed odor protection.Treat your cat to CATSAN® Ultra Odor Hygiene Cat Litter, designed to ensure a clean and odor-free environment for both you and your furry friend. This premium cat litter provides optimal hygiene protection, making it an essential addition to your home.CATSAN® cat litter is engineered to absorb odor before it can develop, ensuring your living space remains fresh. The low-dust, unscented formula provides a clean, natural experience, reducing dust clouds and eliminating artificial scents. Made from highly absorbent Sodium Bentonite, this cat litter sand features unique mineral granules that offer guaranteed odor protection, ensuring a dry and pleasant environment for your cat.As a trusted brand committed to your pet\'s well-being, this cat litter sand delivers reliable hygiene solutions that enhance your cat\'s daily comfort and peace of mind.🐈High-Quality Ingredients 🐈Sodium Bentonite📦In the Package 📦● 1 bag CATSAN® Ultra Odor Hygiene Cat Litter 10LCATSAN® cat litter is more than just a product – it\'s a way to ensure your cat\'s living area is always clean and fresh. Trust CATSAN® for a hygienic, odor-free home environment.', 397.00, 34, '/static/uploads/products/47ae8220959f4de4b5d9cd7c4e99d070_c4bfa36e-d46a-41a3-a04c-af7089d68614.jpg', 'active', '2025-11-24 00:20:09', '2025-11-24 00:20:09', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'catsan-ultra-odor-cat-litter-sand-for-cats-of-all-ages-10l', NULL, NULL, NULL, NULL),
(53, 8, 2, 'CATSAN LIGHT CAT SAND 3L', 'Catsan Ultra Odor Control Formula\r\n\r\nUltra Deodorizing\r\n\r\nUltra Absorbency\r\n\r\nUltra Clumping\r\n\r\nCatsan Ultra Odor Control Cat Litter is a quality cat litter made from naturally occurring Sodium Bentonite. A hygienic, handy and effective answer to controlling odors. When wet, the clay particles quickly absorb moisture and odors and form small well-defined clumps.\r\n\r\nCatsan Ultra Odor Control Cat Litter is easily removed prolonging the life of the litter while leaving the tray clean and fresh.\r\n\r\nCatsan Ultra Odor Control Cat Litter is hygienic, handy and very economical. If pet waste is removed daily, the remaining litter will not need to be discarded. Simply top up with Catsan to the recommended depth.', 200.00, 323, '/static/uploads/products/faaeabfc71634e7d9f23ec348d4c3d84_d96e2dfa-8d8c-4335-a9f9-8bbd8daa6e89.jpg', 'active', '2025-11-24 00:22:46', '2025-11-24 00:22:46', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'catsan-light-cat-sand-3l', NULL, NULL, NULL, NULL),
(54, 8, 2, 'Cat Pet Bath Brush Pet Grooming  Massage Brush with Shampoo Dispenser Soft Silicone Brush', 'The pet steam comb is a must-have addition to your pet care routine, combining hair removal, cleaning, and massaging functions to keep your cat looking and feeling great.\r\n\r\n🐾【Rechargeable Spray Function】\r\n\r\nThe pet steam comb can say goodbye to static electricity and effortlessly remove dust and dirt from your pet\'s fur. You can add water, softener or deodorant to the water tank, and the resulting spray can effectively avoid static electricity and excess hair flying around when grooming pets. The dander and loose hair combed from pets will all be collected on the comb.\r\n\r\n🐾【Silicone Brush Teeth】\r\n\r\nThe smooth rounded teeth head provides a better massage experience, while the silicone brush teeth effectively stick to and remove fallen hair. Pet steam brush the tapered spiral design easily tackles messy hair and is tough enough to handle any hair type.\r\n\r\n🐾【180° Rotating Handle】\r\n\r\nThe rotating handle that allows you to easily brush all areas of your cat. The removable steamy pet comb head makes cleaning a breeze, and its lightweight design ensures comfort during extended grooming sessions.\r\n\r\n🐾【Easier Cleaning】\r\n\r\nCats absolutely hate being drenched in water , but with this pet steam comb with steamer, you\'re guaranteed to have a sure-fire way to clean them up without getting any scratches or bites from your bath-hating pet!', 108.00, 32, '/static/uploads/products/8d0934c2977441418f776f5a0b1b1d5a_d363209a-0316-4e6f-a5d6-5e8fbbb7cb72.jpg', 'active', '2025-11-24 00:32:38', '2025-11-24 00:32:38', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'cat-pet-bath-brush-pet-grooming-massage-brush-with-shampoo-dispenser-soft-silicone-brush', NULL, NULL, NULL, NULL),
(55, 8, 2, 'Dog Bed Mat Cat Bed Dog Bed Washable Sleeping Warm Soft Pet Mat Cat Mat Bed For Dogs', 'his product is a washable pet bed mat designed to serve as a comfortable resting or sleeping spot for both cats and dogs. It’s made for pets who love to curl up, nap, or lounge, offering a soft, warm, and cozy surface while being easy to clean and maintain.\r\n\r\nKey Features:\r\n\r\nMaterial & Comfort: Soft fabric (typically polyester, faux fur, or plush) plus PP cotton or other padding ensures a comfortable, cushiony surface that’s gentle on pets’ bodies. \r\nTikTok Shop\r\n+2\r\nLazada\r\n+2\r\n\r\nWashable Design: The mat is machine-washable (or hand-washable depending on model) so you can keep it clean, hygienic, and odor-free. \r\nLazada\r\n\r\nWarmth / Insulation: Some mats have insulating materials to retain heat, making them especially good for colder weather or pets who like a warm nest. \r\nLazada\r\n+1\r\n\r\nNon-slip / Stable Base: Designed to stay in place so your pet\'s mat doesn’t slide around. \r\nLazada\r\n\r\nMultiple Sizes: Comes in various sizes to fit different pets (small, medium, large) and different spots (crate, floor, couch). \r\nLazada\r\n+1\r\n\r\nLightweight & Portable: Easy to move around, can be used inside cages, on floors, or even for travel.', 342.00, 65, '/static/uploads/products/d7c484f41a024d6d9a6c90a4b775e0be_e630b363-713e-4608-ad32-0c7be066fe30.jpg', 'active', '2025-11-24 00:34:17', '2025-11-24 00:34:17', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'dog-bed-mat-cat-bed-dog-bed-washable-sleeping-warm-soft-pet-mat-cat-mat-bed-for-dogs', NULL, NULL, NULL, NULL),
(56, 8, 2, '2 in 1 Pet Bowl with Tray Cat Automatic Drinking Feeder Dog Feeding Bowls', '【Prevent Spilling, Groove Design】: This dog feeding station is perfect design for raised lip edge keeping the water & food spills to a minimum, don\'t have to worry about soiling the floor when feeding your pets, and it can save food at the same time.\r\n\r\n【Anti-Slip】: There are anti-slip rubber suction cups on the bottom to keep the bowl steady and prevents it from sliding around while the pets is drinking and eating.\r\n\r\n【Safe & Nontoxic Material】: Stainless bowl + PP bowl base + Non-toxic plastic bottle. Protect your pet\'s health.\r\n\r\n【Easy to Clean】：The stainless steel bowls and water dispenser bottle are removable, easy to get and clean. The bowls and water bottle had better be quickly rinsed or wiped clean after each use.\r\n\r\n\r\n\r\n\r\n\r\nColor: Blue/Green/Pink\r\n\r\nMaterial: PP+HIPS+Stainless Steel\r\n\r\nStand-34*20CM/13.4\"*7.9\"(LW)\r\n\r\nCapacity of Water Bottle: 500ml\r\n\r\nFood Bowl: 5.5\"*1.6\"\r\n\r\nTarget-audience: Cats, Small Medium Dogs,Puppy Kitten, Rabbits\r\n\r\nMatters Need Attention', 162.00, 22, '/static/uploads/products/43b0ca08582249a28bf45af271976e94_55789241-6028-4982-a24f-8d92713a9189.jpg', 'active', '2025-11-24 00:36:40', '2025-11-24 00:36:40', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, '2-in-1-pet-bowl-with-tray-cat-automatic-drinking-feeder-dog-feeding-bowls', NULL, NULL, NULL, NULL),
(57, 8, 4, 'Bird Snack For Parrots Nutrient Grain Snack Wheat Ears Snack Treat Bird Cage For Bird Toys', '❤ Product Specification ❤\r\n\r\n\r\n\r\n☆ Product Name: Bird Grain Food Bar\r\n\r\n☆ Product Material: 100% Natural Grains\r\n\r\n☆ Product Color: Multicolor (varies by flavor)\r\n\r\n☆ Suitable For Pets: Parrots, Budgies, Lovebirds, Cockatiels, and other small to medium birds\r\n\r\n☆ Shelf Life: 6–12 months (store in a cool, dry place)\r\n\r\n☆ Weight: Approx. 30–50 grams per bar\r\n\r\n☆ Size: Approx. 3 x 2 x 14 cm or 3.5 x 2.5–3 x 15 cm (size may vary)\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆ Made with natural honey – no additives, sugar, or glue\r\n\r\n☆ Packed with vitamins, minerals, and trace nutrients\r\n\r\n☆ Encourages chewing, beak grinding, and boredom relief\r\n\r\n☆ Easy cage attachment with a metal hook for safety\r\n\r\n☆ Portable design, perfect for home or outings\r\n\r\n\r\n\r\n❤ Package Includes ❤\r\n\r\n✔︎ 1 x Bird Grain Food Bar', 87.00, 45, '/static/uploads/products/a421e3bebd6c4c828deff3d3a3fcfd76_c7d89c1b-0dbf-4443-81b6-ec986cdca1b5.jpg', 'active', '2025-11-24 00:42:54', '2025-11-24 00:42:54', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'bird-snack-for-parrots-nutrient-grain-snack-wheat-ears-snack-treat-bird-cage-for-bird-toys', NULL, NULL, NULL, NULL),
(58, 8, 4, '1200ml Bird Food For Bird Toys Bird Seed Mix Parrot Food Bird Feeder And Drinker Bird Cage', '❤ Product Specification ❤\r\n\r\n\r\n\r\n☆ Product Name:  Bird Food\r\n\r\n☆ Suitable For Pets: Bird/Parrot/ETC.\r\n\r\n☆ Shelf Life：18 Months\r\n\r\n☆ Weight: 1200ml\r\n\r\n☆ Size: 9.5 x 10.5 x 15 cm\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆ BRIGHT FEATHERS     \r\n\r\n☆ EASY TO DIGEST    \r\n\r\n☆ STRONG BONES   \r\n\r\n☆ PROMOTE BRAIN DEVELOPMENT   \r\n\r\n☆ NATURAL PROTECTION     \r\n\r\n\r\n\r\n❤ Package Include ❤\r\n\r\n\r\n\r\n✔︎ 1 x 1200ml Bird Food', 199.00, 535, '/static/uploads/products/7c7be06f2b6d4f8aa1ff9361e90c9b70_517befbc-8198-4fed-8340-3b72dfebb789.jpg', 'active', '2025-11-24 00:45:51', '2025-11-24 00:45:51', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, '1200ml-bird-food-for-bird-toys-bird-seed-mix-parrot-food-bird-feeder-and-drinker-bird-cage', NULL, NULL, NULL, NULL),
(59, 8, 4, 'African Mix Bird Food Bird Seed Food Seed Blend All Stages Pet Food Essential', '🌟 Premium Nutrition for Your Feathered Friends! 🌟\r\n\r\n\r\n\r\nOur African Bird Seed Mix is crafted to provide complete daily nutrition for your beloved birds. Packed with a rich variety of seeds and grains, this mix supports energy, beak health, and vibrant feather condition. It\'s perfect for all life stages, from chicks to seniors, ensuring your birds stay healthy and happy.\r\n\r\n\r\n\r\n🦜 Suitable for a Variety of Birds 🦜\r\n\r\n\r\n\r\nThis seed mix is ideal for African Greys, Lovebirds, Senegals, and more! Whether you have a small budgie or a large parrot, our mix caters to their nutritional needs.\r\n\r\n\r\n\r\n📦 Available Variations 📦\r\n\r\n\r\n\r\nChoose the perfect size for your needs:\r\n\r\n- 500g\r\n\r\n- 1kg\r\n\r\n\r\n\r\n🌱 Natural & Clean Ingredients 🌱\r\n\r\n\r\n\r\nOur seed mix is free from artificial colors and preservatives, ensuring a natural and clean diet for your birds. Serve it in a clean dish and replace uneaten food daily to maintain hygiene.\r\n\r\n\r\n\r\nGive your birds the best with our African Bird Seed Mix and watch them thrive! 🌟', 47.00, 453, '/static/uploads/products/3d47a742db1d4cd4ad8bfd316ffbf56a_3960afb7-8dc2-487f-ae17-6b63c7f7a4bb.jpg', 'active', '2025-11-24 00:47:02', '2025-11-24 00:47:02', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'african-mix-bird-food-bird-seed-food-seed-blend-all-stages-pet-food-essential', NULL, NULL, NULL, NULL),
(60, 8, 4, 'Bird Hanging Cage Ceramic Bowl For Bird Feeder For Bird Drinker For Bird Toys For Bird Perch', '❤ Product Specification ❤\r\n\r\n\r\n\r\n☆ Product Name: Bird Hanging Ceramic Bowl\r\n\r\n☆ Product Material: Ceramic\r\n\r\n☆ Product Color: Blue Green Pink Yellow\r\n\r\n☆ Suitable For Pets: Universal for Birds\r\n\r\n☆ Size: 8 x 8 x 5 CM\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆ Holds water, food, and snacks.\r\n\r\n☆ The elevated design reduces cervical strain.\r\n\r\n☆ High-temperature ceramic is non-absorbent and stain-resistant.\r\n\r\n☆ Available in multiple colors to match your home decor.\r\n\r\n\r\n\r\n❤ Package Include ❤\r\n\r\n✔︎ 1 x Ceramic Bowl', 47.00, 3434, '/static/uploads/products/121d718d7f2c4553b0ab9582714018cf_e9662b09-1407-40c6-9dab-0fb9d9b9a7c0.jpg', 'active', '2025-11-24 00:48:39', '2025-11-24 00:48:39', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'bird-hanging-cage-ceramic-bowl-for-bird-feeder-for-bird-drinker-for-bird-toys-for-bird-perch', NULL, NULL, NULL, NULL),
(61, 8, 4, 'Baby Bird Feeding Syringe with Spoon – Handfeeding Feeder for Parrots and Young Birds', '● High quality of materials.\r\n\r\n● Lightweight and high heat resistance.\r\n\r\n● Not easy to break and durable.\r\n\r\n● Suitable for feeding, epidemic prevention and treatment.\r\n\r\n● Two capacities are available to choose from, depending on your needs.\r\n\r\n● 2mm anti-dropping silicone hose, using high-quality silicone\r\n\r\n● High-quality milk spoon made of metal, resistant to temperature and cold, not easy to damage\r\n\r\n\r\n\r\nSpecification:\r\n\r\nType: Parrot Feeding Syringe\r\n\r\nMaterial: Plastic\r\n\r\nCapacity: 10ML/20ML/30ML/50ML/100ML\r\n\r\nOptional Type: With Spoon / Without Spoon\r\n\r\nColor: As pictures shown\r\n\r\nSize: 20MLSyringe:app.13.7 x 5.8 cm\r\n\r\nMilk Spoon:12cm\r\n\r\nPackage includes:\r\n\r\n\r\n\r\n1 x Parrot Feeding Syringe （With Spoon / Without Spoon）', 47.00, 56, '/static/uploads/products/d467f2253e864071a27a83f0b1bead6a_215b18da-e8c3-4766-a36d-566b70a71987.jpg', 'active', '2025-11-24 00:49:42', '2025-11-24 00:49:42', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'baby-bird-feeding-syringe-with-spoon-handfeeding-feeder-for-parrots-and-young-birds', NULL, NULL, NULL, NULL);
INSERT INTO `products` (`id`, `seller_id`, `category_id`, `name`, `description`, `price`, `stock_quantity`, `image_url`, `status`, `created_at`, `updated_at`, `sku`, `weight`, `dimensions`, `brand`, `age_group`, `pet_type`, `featured`, `seller_latitude`, `seller_longitude`, `low_stock_threshold`, `meta_title`, `meta_description`, `meta_keywords`, `slug`, `sale_price`, `sale_start_date`, `sale_end_date`, `cost_price`) VALUES
(62, 8, 4, 'Bird Feeder Hanging Bowl for Cage Automatic Food Dispenser Parrot Feeding Bird Parrot Accessories', 'Experience hassle-free bird feeding with our Automatic Bird Feeder, designed to make your life easier and keep your pet birds happy! The automatic dispenser ensures your birds always have access to food, while the transparent hopper lets you easily monitor food levels at a glance. Cleaning is a breeze with the detachable design, and the front pole helps prevent food spillage, keeping your cage neat and tidy.\r\n\r\n\r\n\r\nChoose Your Perfect Fit:\r\n\r\n- Available in multiple types to suit your bird’s needs and your feeding preferences.\r\n\r\n\r\n\r\nWhy You\'ll Love It:\r\n\r\n- Automatic food dispensing for consistent feeding\r\n\r\n- Easy to clean and refill for daily convenience\r\n\r\n- Prevents food spillage and keeps the cage clean\r\n\r\n\r\n\r\nPerfect for a variety of bird species, this feeder is a must-have for any bird owner looking for a reliable and easy-to-use feeding solution. Make feeding time simple, clean, and stress-free for both you and your feathered friends!', 199.00, 97, '/static/uploads/products/b1dc6d1dab3b4cc8898a260e0e105203_f6751718-00cb-42a2-b4b5-58bbf1b0e836.jpg', 'active', '2025-11-24 00:51:44', '2025-11-25 08:49:39', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'bird-feeder-hanging-bowl-for-cage-automatic-food-dispenser-parrot-feeding-bird-parrot-accessories', NULL, NULL, NULL, NULL),
(63, 8, 4, 'Bird Feeder White Bowl', 'Features:\r\n\r\n❀Parakeet Feeder Box\r\n\r\n❀2 in 1 type of feeder can store water or food,which is convenient for \r\n\r\n  pet to eat or drink. Both can hold food, but also can hold water.\r\n\r\n❀Rear hooks can be hung without being knocked out or broken. It can \r\n\r\n   be hung on a cage,usually can also be used as a feeder used for food.\r\n\r\n❀The front double rods design is convenient for birds to drink and eat\r\n\r\n\r\n\r\n❀Using high quality plastic material, safety and health, tasteless and \r\n\r\n  durable. Easy to use and clean.\r\n\r\n❀Suitable for the bird, parrots,pigeons etc.\r\n\r\n\r\n\r\nSpecifications:\r\n\r\n※Name:Pet Cage Plastic Food Container Parrot Birds Water Hanging \r\n\r\n   Bowl Parakeet Feeder Box\r\n\r\n※Material: Plastic\r\n\r\n※Size：App.21x5x6.5cm/8.27x1.97x2.56in\r\n\r\n※Color:White\r\n\r\n\r\n\r\nPacking list: 1xpc\r\n\r\n\r\n\r\n►Like and follow us will get extra coupons!\r\n\r\n►Please do not ask for a refund lightly, contact customer service \r\n\r\n   will give you a satisfactory answer\r\n\r\n►Choose the variation of the item correctly to avoid any mistake \r\n\r\n►Free shipping, please collect the free shipping coupon on the \r\n\r\n   shopee homepage\r\n\r\n\r\n\r\nNotes:\r\n\r\n※The size is measured by hands, please allow minor error of measurement. \r\n\r\n※Photo color might be a little different from the actual product due to color display of different monitors.', 199.00, 65, '/static/uploads/products/21f1c02aa7fb4ba5a757dddeca02e9b1_1423067e-d3e8-4652-9c5b-0edef37f9281.jpg', 'active', '2025-11-24 00:53:16', '2025-11-24 00:53:16', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'bird-feeder-white-bowl', NULL, NULL, NULL, NULL),
(64, 8, 4, 'Bird Feeder Hanging Cage', 'Welcome to the world of convenience with our Durable & Easy-to-Clean Automatic Bird Water Dispenser and Feeder - Large Capacity! This is the perfect solution for keeping your feathered friends happy and healthy.\r\n\r\n\r\n\r\nApplication:\r\n\r\nThis versatile dispenser and feeder is designed for easy attachment to any birdcage. It\'s ideal for a wide range of birds, including parrots, pigeons, chickens, ducks, and other poultry. Simply hang it up, and you\'re good to go!\r\n\r\n\r\n\r\nFeatures:\r\n\r\n- Crafted from robust plastic, this product promises durability and safety for your beloved pets.\r\n\r\n- With a generous capacity of 140~150ml, it efficiently serves both water and feed.\r\n\r\n- Made from eco-friendly materials, it ensures a safe and healthy environment for your birds.\r\n\r\n- The removable design makes cleaning a breeze, ensuring your birds always have fresh water and food.\r\n\r\n\r\n\r\nImportant Notes:\r\n\r\n- Manual measurements are used, so slight variations in size may occur.\r\n\r\n- Due to different monitor settings, the product color may appear slightly different.\r\n\r\n\r\n\r\nThis bird cage accessory is a must-have for any bird owner, providing a practical and efficient way to care for your avian companions. Make your bird care routine easier and more enjoyable with this fantastic product!', 23.00, 86, '/static/uploads/products/e2ebf5ddb1e54dd7958ffbfb79e5b002_fcc1d112-074b-4db4-8f63-ed737cc8de90.jpg', 'active', '2025-11-24 00:54:55', '2025-11-24 00:54:55', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'bird-feeder-hanging-cage', NULL, NULL, NULL, NULL),
(65, 8, 3, 'Artificial Bucket Cave Fish Tank Landscape Aquarium Wine Bucket Boat Volcanic Resin Decoration', 'This is a multi‑themed aquarium ornament combining volcanic rock aesthetics, broken barrels or wine‑bucket themes, and boat or cave structures, all crafted from resin. It functions both as a decorative landscape piece and a hiding spot / shelter for fish.', 28.00, 432, '/static/uploads/products/f020a002dcf44fbc88b81804ec5934e2_ba8660c4-df34-4627-aca1-ecfdbd105986.jpg', 'active', '2025-11-24 00:57:19', '2025-11-24 00:57:19', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'artificial-bucket-cave-fish-tank-landscape-aquarium-wine-bucket-boat-volcanic-resin-decoration', NULL, NULL, NULL, NULL),
(66, 8, 3, 'Artificial Miniature Coral Craft Aquarium Decorations Resin Starfish Ornaments for Fish Tanks', 'Product Description\r\n\r\nWe ship from Manila within 48 hours!\r\n\r\nWe are shopee\'s lowest price!\r\n\r\nWe accept wholesale!\r\n\r\nWe accept returns if the item is not yet worn or used.     \r\n\r\n  \r\n\r\nAttention: please check the picture of the order options carefully, and choose what you like.\r\n\r\n\r\n\r\nSpecification:\r\n\r\nModel: Home Garden Aquarium Mini Coral Decoration\r\n\r\nColor: Show as the picture\r\n\r\nMaterial: Resin\r\n\r\nSize:  It is mini coral decoration. Please check the sizes in the pictures carefully,  before you order.\r\n\r\n\r\n\r\nPackage include:\r\n\r\n1x Aquarium Coral Decoration  \r\n\r\n  \r\n\r\n Notes:\r\n\r\n Due to the light and screen setting difference, the items color may be slightly different from the pictures.\r\n\r\n Please allow slight dimension difference due to different manual measurement.', 28.00, 23, '/static/uploads/products/4cf97184281541b599e525bd6203c130_710011f6-fbf6-42de-91af-14f09123d9f9.jpg', 'active', '2025-11-24 00:58:09', '2025-11-24 00:58:09', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'artificial-miniature-coral-craft-aquarium-decorations-resin-starfish-ornaments-for-fish-tanks', NULL, NULL, NULL, NULL),
(67, 8, 3, 'Clear Plastic Desktop Fish Tank Mini Aquarium for Goldfish-Super White Transparent Home Decor', '🌊 3-in-1 Smart System\r\n\r\nSilent pump + waterfall filter + soft LED lighting – Auto-clean technology reduces 70% maintenance time\r\n\r\n\r\n\r\n📐 Space-Saving Design\r\n\r\nPerfect for:\r\n\r\n▫️ Office desks (18x18cm mini size)\r\n\r\n▫️ Bedside tables\r\n\r\n▫️ Condo living spaces\r\n\r\n▶ Holds 2L water (Ideal for 1 Betta/3 Guppies)\r\n\r\n\r\n\r\n💎 Zero Residue Guarantee\r\n\r\nPatented waterfall filtration removes 95% impurities – Enjoy aquarium-grade water clarity 24/7\r\n\r\n\r\n\r\n🐟 Beginner-Friendly Kit\r\n\r\n\r\n\r\n🔥 PH Market Exclusive\r\n\r\n1-YEAR warranty + Free replacement parts', 28.00, 4, '/static/uploads/products/f4f2322660e34e4996a34e4b3fe242c5_aa3685a4-c9b0-4ba3-aaf1-b2ae1806f407.jpg', 'active', '2025-11-24 00:59:06', '2025-11-24 00:59:06', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'clear-plastic-desktop-fish-tank-mini-aquarium-for-goldfish-super-white-transparent-home-decor', NULL, NULL, NULL, NULL),
(68, 8, 3, 'Filter Small Tank Filter Suspension Oxygen Pump 3 in 1 Small Aquarium', 'Three-in-one submersible pump, oxygen pump, small fish tank, external waterfall filter equipment, water purifier\r\n\r\n \r\n\r\n【Feature】\r\n\r\n✅Multifunctional Filter: Filtration, Oxygen Aeration, and Clearing Oil Slick.\r\n\r\n✅This filter is made to hang on the back of your aquarium where space is limited, and the built-in sponge keeps excellent ✅biochemical and physical filtration.\r\n\r\n✅With a surface skimmer, while filtering the water, it skims the oil slick off the water surface.\r\n\r\n✅It also has added enough oxygen for the tank due to the design ✅with the water circulation system and returning water cascade.\r\n\r\n✅It has an adjustable flow rate and is easy to install, uninstall and maintain.          \r\n\r\n✅Optimal flow is realized by an adjustable flow regulating valve.\r\n\r\n✅240L of water output per hour, suitable for fish tanks under 12 liters.\r\n\r\n✅All the parts are detachable.\r\n\r\n\r\n\r\n【Specification】\r\n\r\n✅Material: Acrylic \r\n\r\n✅Power: 3W \r\n\r\n✅Max Flow Rate: 240L/H\r\n\r\n✅Voltage: 220V, 110V\r\n\r\n\r\n\r\n【Package included】\r\n\r\n✅1* filter\r\n\r\n✅1* bio-sponge\r\n\r\n✅1* water inlet pipe\r\n\r\n✅2* extension tubes\r\n\r\n✅1* surface skimmer\r\n\r\n\r\n\r\n#filter#externalfilter#waterfilter#aquariumfilter#waterfallfilter#circulation#transparent #aquarium#hydroponicsupplies#fishtank#\r\n\r\nfish tank#water pump#water filter aquarium#\r\n\r\n\r\n\r\n【Note】\r\n\r\n✅Fill with water before using this filter.\r\n\r\n\r\n\r\n【Why You Should Need An Aquarium Filter】\r\n\r\n✅The water quality in the aquarium is an uncertain and dynamic environment. Filters keep the water in your aquarium clean by removing debris and toxins like ammonia, and nitrates. It can help oxygenate the water by creating surface agitation.', 30.00, 10, '/static/uploads/products/770ebab0dc38488f84aa11bea4fd4694_bdb7acad-5eaa-4779-bb5b-c0f26c45e11c.jpg', 'active', '2025-11-24 01:00:19', '2025-11-24 01:00:19', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'filter-small-tank-filter-suspension-oxygen-pump-3-in-1-small-aquarium', NULL, NULL, NULL, NULL),
(69, 8, 3, 'Fish Tank Plastic High Transparency Fish Tank Small Fish Tank Indestructible Home Office Decoration', '💕Features:\r\n1. Made of PET material, it has the characteristics of transparency, so that you can clearly observe the living state of fish and turtles.\r\n2.Easy maintenance: Round design, no dead corners, easy to clean and maintain. Give you more convenience to clean.\r\n3.Fall resistant: Made of strength PET material, this plastic fish bowl is fall resistant, durable, has lasting service life.\r\n4.Multifunctional: not only can you raise goldfish, but also can raise small turtles and other reptiles, very practical.\r\n5.The Small Fish bowl is good for decorating home, shop, shopping mall and office, beautify and purify your living environment.\r\n\r\n\r\n\r\nTransparent Round Fish Tank Fish Bowl Desktop Aquarium Bowl Clear Plastic Portable Small creative light luxury Living Room Home Office living desk small aquariums small ornamental fish Home Decor Good View', 36.00, 2, '/static/uploads/products/5dd9119b395247fe8db00aaae3a3516a_de4b96f5-fd09-4ccc-b05e-0cf90c9d9577.jpg', 'active', '2025-11-24 01:03:12', '2025-11-24 01:03:12', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'fish-tank-plastic-high-transparency-fish-tank-small-fish-tank-indestructible-home-office-decoration', NULL, NULL, NULL, NULL),
(70, 8, 3, 'Fish Food YUMIMA Betta Fish Food Beta Feed Tropical', 'Pellet Type: Floating\r\n\r\nWeight: 28g/100g\r\n\r\nProduct Features:\r\n\r\n- High-grade quality feed food consists of essential nutrients and vitamins needed to keep the pet healthy\r\n\r\n- A growth type basic diet to meet the requirement of all nutrients.\r\n\r\n- Balanced nutrition to maintain good growth performance\r\n\r\nDirections:\r\n\r\n1.Reduce feeding amounts the day before and after changing the water.\r\n\r\n2.If mold or degradation is discovered within the expiry date, please stop using the product and contact us immediately.\r\n\r\n3.After unpacking, please run out as soon as possible to avoid degradation.\r\n\r\n\r\n\r\nNotes:\r\n\r\nDue to the light and screen setting difference, the items color may be slightly different from the pictures.\r\n\r\nPlease allow slight dimension difference due to different manual measurement.', 28.00, 43, '/static/uploads/products/ce49a6b326404897a9c1a2133a6f1734_ad91a09e-027e-4ad3-9afd-9b466a4ee575.jpg', 'active', '2025-11-24 01:05:42', '2025-11-24 01:05:42', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'fish-food-yumima-betta-fish-food-beta-feed-tropical', NULL, NULL, NULL, NULL),
(71, 8, 3, 'Betta Food 25g fish food', 'High-protein 25 g betta food pellets to support growth, vibrant colors, and overall health of your betta fish. Easy-to-feed and nutritionally balanced for daily use.', 69.00, 43, '/static/uploads/products/ce124076a7584e57a46cdcbba5ef9902_a973da83-9546-475a-b893-aa8f296b7b26.jpg', 'active', '2025-11-24 01:07:45', '2025-11-24 01:07:45', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'betta-food-25g-fish-food', NULL, NULL, NULL, NULL),
(72, 8, 3, 'Aquarium Filter Complete Set Submersible Water Pump Sponge Filter For Aquarium Oxygen For Aquarium', 'Keep your aquarium environment clean and healthy with our Aquarium Sponge Filter Kit! Designed for efficient oxygenation and filtration, this kit is perfect for maintaining optimal water quality for your fish and plants. Enjoy peace of mind knowing your aquatic life is supported by a reliable filtration system.\r\n\r\n\r\n\r\nAvailable Variations:\r\n\r\n- Size: 2 Boxes\r\n\r\n- Size: 3 Boxes\r\n\r\n- Size: 4 Boxes\r\n\r\n- Size: 5 Boxes\r\n\r\nChoose the size that best fits your aquarium needs, whether you have a small or large setup.\r\n\r\n\r\n\r\nWhy Choose This Kit?\r\n\r\n- Efficient oxygenation ensures your fish get the air they need.\r\n\r\n- Easy maintenance makes cleaning and upkeep simple.\r\n\r\n- Suitable for various aquarium sizes, offering flexibility for different setups.\r\n\r\n\r\n\r\nAdditional Information:\r\n\r\nEach kit includes a submersible water pump and sponge filter, providing a complete solution for aquarium filtration. Select the size that matches your aquarium for the best results and enjoy a thriving aquatic environment!', 284.00, 24, '/static/uploads/products/e7a021dc3c874737a27adb3e0f407282_7b9cc249-52ff-4c6d-bb68-dd173b13c14e.jpg', 'active', '2025-11-24 01:09:00', '2025-11-24 01:09:00', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'aquarium-filter-complete-set-submersible-water-pump-sponge-filter-for-aquarium-oxygen-for-aquarium', NULL, NULL, NULL, NULL),
(73, 8, 3, 'Aerator Fish Breeding Air Pump Silent Portable Aquarium Fish Tank Portable Mini USB Oxygen Pump', 'Applicable scenarios: Fish tanks less than 60 cm/air regulators less than 30 cm；\r\n\r\nColor: blue, grass green, light blue, black, red, yellow；\r\n\r\nSize:8*3 CM；\r\n\r\nMaterial: Silicone；\r\n\r\nPower: 1 W；\r\n\r\nVoltage: Anything that can charge a mobile phone is universal；\r\n\r\nExhaust volume: 1 .0 L；\r\n\r\n\r\n\r\nFeatures:\r\n\r\n1.Powerful, safe and reliable performance, large exhaust volume. You can feel comfortable to buy and use it.\r\n\r\n2.Longer use time, 24 hours of continuous use.You can enjoy the happy time of fishing.\r\n\r\n3.USB interface is more convenient,small and portable and everyone can operate it.It is suitable for outdoor.Wide use is the biggest reason that it is popular by people.\r\n\r\n4.Mute.In the living room, bedroom, office and other quiet environment, there is no sound and can provide a better using experience for you.\r\n\r\n\r\n\r\nPackage Include:\r\n\r\n1 x air pump\r\n\r\n1 x air tube\r\n\r\n1 x air stone\r\n\r\n\r\n\r\nManual measurement may be different from 1-2 cm. The colors deviation might differ due to different monitor settings, please kindly understand.', 40.00, 23, '/static/uploads/products/376a28375638426f8228c4917b8a4470_6ac990fc-2724-47b0-baef-95294f6df661.jpg', 'active', '2025-11-24 01:10:52', '2025-11-24 01:10:52', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'aerator-fish-breeding-air-pump-silent-portable-aquarium-fish-tank-portable-mini-usb-oxygen-pump', NULL, NULL, NULL, NULL),
(74, 8, 3, 'Fish Tank Scenery Decoration Simulation Aquatic Plants Aquarium Landscaping Fake Aquatic Plants', '🍬🍬🍬Buying Guide🍬🍬🍬\r\n\r\n👍DELIVERY PERIOD: 1-2 days Metro Manila,3-4 days Provincial\r\n\r\n💰💸COD: All the listed products are supported by cash on delivery\r\n\r\n💗ALL ITEMS ARE AVAILABLE UNLESS MARKED AS \"SOLD OUT\"\r\n\r\n🏭We not only provide competitive prices, but also time delivery and quality assurance;\r\n\r\n🍬CHOOSE THE CORRECT VARIATION IF THE ITEMS HAS DIFFERENT COLORS/PRINTS SO WE CAN AVOID MISTAKES\r\n\r\n👍WE ACCEPT RETURNS IF THE ITEM IS NOT YET WORN OR USED.', 40.00, 244, '/static/uploads/products/1648f6526c5147c297127b42c8e1e781_9564cfb8-7e1d-4d48-bd5a-40ce1729bb2d.jpg', 'active', '2025-11-24 01:12:01', '2025-11-24 01:12:01', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'fish-tank-scenery-decoration-simulation-aquatic-plants-aquarium-landscaping-fake-aquatic-plants', NULL, NULL, NULL, NULL),
(75, 8, 3, 'Aquarium Fish Net Colorful Round Fish Net Suitable for Peacock Fish, Etc', 'Description: \r\n\r\nColor: blue,green, red, pink\r\n\r\nSize: S, M, L, XL\r\n\r\n\r\n\r\nManual measurement may be different from 1-2 cm. The colors deviation might differ due to different monitor settings, please kindly understand.', 40.00, 244, '/static/uploads/products/8f3700d765a04a87a4ed193ae5ad9c19_507607f0-23b4-4f9e-85b6-5721e79e9e05.jpg', 'active', '2025-11-24 01:14:02', '2025-11-24 01:14:02', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'aquarium-fish-net-colorful-round-fish-net-suitable-for-peacock-fish-etc', NULL, NULL, NULL, NULL),
(76, 8, 3, 'Betta Fish Tank Mini Aquarium Block Guppy Fish Tank', 'Product Name: fish tank\r\n\r\nColor:  black cylinder,  transparent cylinder\r\n\r\nSize:12*8*10.5cm\r\n\r\nWeight :145 g\r\n\r\nSize: small\r\n\r\nMaterial: plastic\r\n\r\n\r\n\r\nPacking list:\r\n\r\n1 *Mini fish bowl', 79.00, 978, '/static/uploads/products/a9fa010ac74f4c7eb5a9d78355d1512f_1194d82b-0c02-490b-ae3a-944dbe387950.jpg', 'active', '2025-11-24 01:15:04', '2025-11-24 01:15:04', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'betta-fish-tank-mini-aquarium-block-guppy-fish-tank', NULL, NULL, NULL, NULL),
(77, 8, 5, '120ml Pet Flea Spray Dog Cat Tick and Flea Removal Spray', '120 ml insect‑control spray for dogs and cats — effectively removes and repels fleas, ticks, and lice. Easy-to-use mist formula for direct application on fur, providing fast protection and helping prevent re‑infestation.', 56.00, 5, '/static/uploads/products/db22821dc83040e691f63285feef6898_d982af1e-c3c5-4a30-a7bf-76fedb0e5644.jpg', 'active', '2025-11-24 01:18:23', '2025-11-24 01:18:23', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, '120ml-pet-flea-spray-dog-cat-tick-and-flea-removal-spray', NULL, NULL, NULL, NULL),
(78, 8, 5, 'Pet Nail Clipper', 'Safe and Precise Nail Trimming for Your Pets! ✂️\r\n\r\nGive your furry friends the best care with our pet nail clipper, designed for both cats and dogs. The standout feature is the round hole, which ensures safe and precise trimming every time. The sharp stainless steel blade makes nail cutting quick and effortless, even for beginners. Plus, the comfortable non-slip handle provides a secure grip, so you can groom with confidence!\r\n\r\n\r\n\r\nColor Options to Suit Your Style 🎨\r\n\r\nChoose from several attractive colors to match your preference:\r\n- pink\r\n- blue\r\n\r\nPick the one that best fits your pet’s personality or your grooming kit!\r\n\r\n\r\n\r\nWhy Pet Owners Love This Clipper\r\n\r\n- Round hole for safe, precise trimming\r\n\r\n- Sharp stainless steel blade for efficient cutting\r\n\r\n- Ergonomic, non-slip handle for comfortable use\r\n\r\n- Lightweight and durable—easy to handle for all pet owners', 30.00, 64, '/static/uploads/products/cd465e7e80ea48e7b4004b23d97e5295_716de079-3063-4713-a315-89afc39dca03.jpg', 'active', '2025-11-24 01:21:15', '2025-11-24 01:21:15', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-nail-clipper', NULL, NULL, NULL, NULL),
(79, 8, 5, 'Pet Hair Remover', '❤ Product Specification ❤\r\n☆ Product Name:  Pet Hair Remover\r\n☆ Product Material: ABS + nylon fabric\r\n☆ Product Color: Blue/Red\r\n☆ Suitable For Pets: Pet/Dog/Cat\r\n☆ Weight: 190g/6.7oz\r\n☆ Size: \r\n☆ Brush head size: 19*7cm/ 7.47*2.75inch(L*W)\r\n☆ Handle length: 12cm/4.72inch\r\n\r\n❤ Product Features ❤\r\n\r\n☆ Easy to operate\r\n\r\nThe pet hair remover can be forth and back moved to clean the pet hair cleanly. The roller shape and humanized handle design make it easy to operate the pet hair remover. No complex operation process, the pet hair remover is labor-saving and simple to use.     \r\n\r\n☆ Reusable\r\n\r\nNo problem with replacement and power requirement., press the button to clean the container’s hair, and then the pet hair remover can be used again. You do not have to change the battery or sticker frequently like other products. The pet hair remover is eco-friendly and economical.   \r\n\r\n☆ Portable & Travel Friendly\r\n\r\nThe pet hair remover with a 7.47*2.75inch(L*W) brush head and 4.72inch handle is compact and lightweight, which will not occupy much storage space, and is portable. You can bring it anywhere with you.    \r\n\r\n☆ Durable\r\n\r\nThe pet hair remover adopts high-quality ABS and nylon fabric material, which is wear-resistant and can be used for a long time.  \r\n\r\n☆ Widely usage\r\n\r\nThe pet hair remover is suitable for the hair of cats or dogs, whose strong cleanability can remove the pet hair effectively from sofa, bed, carpet, cloth and etc.     \r\n\r\n❤ Package Include ❤\r\n✔︎ 1 x Pet Hair Remover', 120.00, 8, '/static/uploads/products/050d0c66940943aa9a3afeb44ddfa8b6_09c31e76-26d8-4304-8a86-af4a89e02a10.jpg', 'active', '2025-11-24 01:26:53', '2025-11-24 01:26:53', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-hair-remover', NULL, NULL, NULL, NULL),
(80, 8, 5, 'Pet Hair Brush', '❤ Product Specification ❤\r\n\r\n\r\n\r\n☆ Product Name:  Pet Hair Brush\r\n\r\n☆ Product Material: Plastic\r\n\r\n☆ Product Color: Green/Pink/Blue\r\n\r\n☆ Suitable For Pets: Pet/Dog/Cat\r\n\r\n☆ Size: 13.5 x 15.5 cm\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆ One side hair removal and one side finishing     \r\n\r\n☆ Double-sided.    \r\n\r\n☆ Can be hung\r\n\r\n☆ Not easy to rust ·Moisture and bacteria proof      \r\n\r\n☆ Features a reflective logo and a reflective strip on the chest.     \r\n\r\n\r\n\r\n❤ Package Include ❤\r\n\r\n\r\n\r\n✔︎ 1 x Pet Brush', 35.00, 55, '/static/uploads/products/867bedcfdd7242e48ab7cff5b1b115c1_8283c9f9-99e7-4f6b-bea3-ecdba340ef53.jpg', 'active', '2025-11-24 01:28:05', '2025-11-24 01:28:05', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-hair-brush', NULL, NULL, NULL, NULL),
(81, 8, 5, 'Pet Grooming Hammock', '❤ Product Specification ❤\r\n\r\n\r\n\r\n☆ Product Name:  Pet Grooming Hammock\r\n\r\n☆ Product Material: Flannel\r\n\r\n☆ Product Color: \r\n\r\n☆ Suitable For Pets: Pet/Dog/Cat\r\n\r\n☆ Max Weight: 15kg\r\n\r\n☆ Size: length (measurement: the distance between the front and back legs)\r\n\r\n☆ S: 25cm/9.84in\r\n\r\n☆ M: 30cm/11.81in\r\n\r\n☆ L :35cm/13.77in\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆ Made of soft fabric, comfortable for pets to rely on it.     \r\n\r\n☆ Easy to install: provides you with convenience to hang and fix pets, easy to fix them at any height, make any grooming, trimming easier and safer.   \r\n\r\n☆ Easy to wear: just wrap the hammock on pets through holes, then hang it with hooks to start grooming.   \r\n\r\n☆ Ideal for small dogs, cats, or other pets.  \r\n\r\n☆ Plush fabric, pet wear comfortable, won\'t hurt the skin.     \r\n\r\n\r\n\r\n❤ Package Include ❤\r\n\r\n\r\n\r\n✔︎ 1 x Dog Hammock \r\n\r\n✔︎ 2 x Metal Hooks', 299.00, 0, '/static/uploads/products/02586aeb21d6482597bb3754d9d7b46e_196f1397-6999-4c09-afc1-bc5980779586.jpg', 'active', '2025-11-24 01:56:21', '2025-11-24 01:56:21', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-grooming-hammock', NULL, NULL, NULL, NULL),
(82, 8, 5, 'Pet Finger Brush', '❤ Product Specification ❤\r\n\r\n\r\n\r\n☆ Product Name: Pet Finger Toothbrush\r\n\r\n☆ Product Material: Silicone\r\n\r\n☆ Product Color: Whtie\r\n\r\n☆ Suitable For Pets: Pet/Dog/Cat\r\n\r\n☆ Weight:0.5 g\r\n\r\n☆ Size: 5.5 x 2 cm\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆  This small toothbrush is directly set in the fingers, do pet\'s mouse cleaning work, toothbrush    \r\n\r\n☆  Material is liquid silicone, safety, and environmental protection. \r\n\r\n☆   With a tear resistance,flexible, resistant high temperature,good ventilation,etc.\r\n\r\n☆  pet toothbrush is a small bump on one side, the one side is a small soft strip, give your pet time to clean teeth never hurt them.\r\n\r\n☆  Slightly flexible   \r\n\r\n\r\n\r\n❤ Package Include ❤\r\n\r\n\r\n\r\n✔︎ 1 x Pet Finger Toothbrush', 10.00, 8, '/static/uploads/products/6c85b3f43d614d15bfd0bbac2a1a82de_a121a081-2fe0-4819-abb8-19be76df09b5.jpg', 'active', '2025-11-24 01:58:24', '2025-11-24 01:58:24', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-finger-brush', NULL, NULL, NULL, NULL),
(83, 8, 5, 'Pet bathing bag', '❤ Product Specification ❤\r\n\r\n\r\n\r\n☆ Product Name:  Cat Bathing Bag\r\n\r\n☆ Product Material: Net Surface Material\r\n\r\n☆ Product Color: Pink/Green/Gray/Blue\r\n\r\n☆ Suitable For Pets: Pet/Dog/Cat\r\n\r\n☆ Weight: 30g\r\n\r\n☆ Size: Ordinary: 44*35cm\r\n\r\n☆ Upgrade: 53*30 cm\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆ adjustable cat shower bags; With these bags, you can effectively prevent cats from scratching or biting you while giving your cat a bath.     \r\n\r\n☆ the zipper of the cat bathing bag allows you to release one paw at a time, easy for you to cut nails    \r\n\r\n☆ The 4 adjustable drawstrings can well fix the cat to a comfortable position and prevent its teeth and pointed claws from stretching out and scratching you.   \r\n\r\n☆ There is a handle for you to lift up your cat easily.   \r\n\r\n☆ this breathable net bag is not only suitable for cat bathing but also useful for nail trimming, teeth and ears cleaning, pet examination, calming kittens and puppies, and pet traveling, easy for you to take care of your pet.      \r\n\r\n\r\n\r\n❤ Package Include ❤\r\n\r\n\r\n\r\n✔︎ 1 x Cat Bathing Bag', 20.00, 7, '/static/uploads/products/33d0787fada445dcb5c9455a89500d02_fbd08b57-db59-4d45-82f0-489b053204f2.jpg', 'active', '2025-11-24 02:00:21', '2025-11-25 10:17:28', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-bathing-bag', NULL, NULL, NULL, NULL),
(84, 8, 5, 'Pet Bath Towel', '❤ Product Specifications ❤\r\n\r\n\r\n\r\n☆ Product Name: Pet absorbent towel\r\n\r\n☆ Product Material: Suede\r\n\r\n☆ Product Color: Pink/Green/Blue/Yellow/Purple\r\n\r\n☆ Suitable For Pets: Pet/Dog/Cat\r\n\r\n☆ Weight:0.185 kg\r\n\r\n☆ Size:\r\n\r\n☆ S: 43 cm x 33 cm\r\n\r\n☆ L: 43cm x 66 cm\r\n\r\n\r\n\r\n❤ Product Features ❤\r\n\r\n\r\n\r\n☆ Good for long hair baby pets, help you save time to dry their hair    \r\n\r\n☆ Super-absorbent (high quality, soft and gentle) \r\n\r\n☆ Not-sticky hair  \r\n\r\n☆ After using the towel just Rinse and collect it (keep it wet) \r\n\r\n☆ The towel will become hard like paper when it was dry, but just put it into the water, then it will restore again into soft and gentle.    \r\n\r\n\r\n\r\n❤ Package Include ❤\r\n\r\n\r\n\r\n✔︎ 1 x  Pet absorbent towel', 32.00, 75, '/static/uploads/products/51654f2f8def43e49030e2d97fe9670b_d2e138fe-6eb8-479f-8a2d-9731e2d3deca.jpg', 'active', '2025-11-24 02:01:46', '2025-11-27 14:02:25', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-bath-towel', NULL, NULL, NULL, NULL),
(85, 8, 6, 'Pet Anti-Diarrheal Syrup', 'When pets exhibit the following symptoms, it is advisable to promptly use anti-diarrheal syrup:\r\n\r\n \r\n\r\n1. Vomiting: Pets may expel stomach contents or food residue frequently, with vomit often having a food or distinct odor. Pets may appear uncomfortable and restless.\r\n\r\n2. Diarrhea: Pets may pass loose or watery stools frequently, often with a foul odor. Pets may exhibit redness or pain around the anus.\r\n\r\n3. Bloody or watery stools: Pets\' stools may contain fresh blood or dark red traces, and the stool consistency may be watery, lacking solid matter.\r\n\r\n4. Mucous stools: Pets\' stools may contain mucus, appearing thick and viscous, with mucus or mucous clumps present in the stool.', 268.00, 99, '/static/uploads/products/2b40a20c23754c80bf1d6523149dd6ae_Screenshot_2025-11-24_100457.png', 'active', '2025-11-24 02:06:12', '2025-11-24 02:06:12', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-anti-diarrheal-syrup', NULL, NULL, NULL, NULL),
(86, 8, 6, 'Pet Skin Treatment Spray Dog Cat Antibacterial Fungal Spray Skin Disease Treatment', '🌟 Fast-Acting Relief for Your Pets! 🌟  Our 500ml Pet Skin Care Solution is your go-to spray for addressing a variety of skin issues in both dogs and cats. Whether it\'s fungal infections, allergies, or bacterial infections, this spray provides quick relief from itching, redness, and irritation. Plus, it\'s safe for your furry friends, even if they lick it!  🐾 Safe and Gentle Formula 🐾  - Non-irritating and gentle on your pet\'s skin. - Broad-spectrum antibacterial properties ensure comprehensive care. - Perfect for pets of all sizes and specific skin conditions.  🔄 Variations Available 🔄  - 500ml option suitable for both cats and dogs.  📋 Usage Instructions 📋  For best results, use as directed. Our formula is designed to be effective while ensuring the safety and comfort of your pets. Give your pets the care they deserve with our trusted skin care solution!', 128.00, 54, '/static/uploads/products/ae516aba58cc448e8a1b27ba79666594_c7ef3c10-b90a-467a-a723-3349050125cc.jpg', 'active', '2025-11-24 02:08:33', '2025-11-24 02:08:33', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-skin-treatment-spray-dog-cat-antibacterial-fungal-spray-skin-disease-treatment', NULL, NULL, NULL, NULL),
(87, 8, 6, 'Pet flea comb hair comb dog cat stainless steel needle fur comb', 'The Perfect Grooming Tool for Your Pet! Keep your furry friend looking their best with our Pet Hair Grooming Comb, designed for dogs and cats. This must-have tool helps maintain a healthy, tangle-free coat while making grooming sessions quick and hassle-free.  Why Choose Our Grooming Comb? ✔ Durable & Long-Lasting – Made from high-quality plastic and stainless steel, ensuring strength and reliability for long-term use. ✔ Efficient Grooming – The dense stainless steel needles effectively remove fleas, tangles, and loose fur, keeping your pet’s coat smooth and healthy. ✔ Ergonomic & Comfortable – Featuring a non-slip handle, this comb provides a secure, comfortable grip, reducing hand fatigue during grooming.  Compact & Travel-Friendly At 18cm, this grooming comb is lightweight and portable, perfect for home use or on-the-go grooming.  Product Details Type: Pet hair comb / flea comb Material: Plastic & stainless steel needles Size: 18cm Important Notes 📌 Colors may vary slightly due to lighting and screen settings. 📌 Please allow minor size differences due to manual measurement.  Have questions? Feel free to reach out! We’re here to help you and your pet enjoy a stress-free grooming experience. 🐶🐱✨', 23.00, 6, '/static/uploads/products/9c16e0d20a0246a180fe9a026e0f7951_c706d5ce-e03a-4fcf-ab94-117a491ba203.jpg', 'active', '2025-11-24 02:09:46', '2025-11-24 02:09:46', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-flea-comb-hair-comb-dog-cat-stainless-steel-needle-fur-comb', NULL, NULL, NULL, NULL),
(88, 8, 6, 'Cat & Dog Immune Booster', 'Pet Health Liquid is your go-to solution for enhancing the immune system of your beloved dogs and cats. Designed to help them resist infections and recover faster, this supplement is perfect for pets of all ages. With easy administration, you can give it directly, mix it with food, or add it to their drinking water. 🐶🐱\r\n\r\n\r\n\r\n💧 Available Variations:\r\n\r\n- 60ml\r\n\r\n- 150ml\r\n\r\n- 300ml\r\n\r\n\r\n\r\n📝 Key Ingredients:\r\n\r\n- Glucose Syrup\r\n\r\n- Purified Water\r\n\r\n- Whey Protein Powder\r\n\r\n- Bovine Colostrum\r\n\r\n\r\n\r\n📏 Recommended Usage:\r\n\r\nThe dosage varies by pet size. Use 1-2 times daily for 2-4 weeks to see optimal results. Ensure your furry friends get the best care with Cassiel Pet Health Liquid! 💪', 130.00, 84, '/static/uploads/products/5b03a79ea505425498a8022b7aa64e19_Screenshot_2025-11-24_104853.png', 'active', '2025-11-24 02:50:25', '2025-11-27 22:37:14', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'cat-dog-immune-booster', NULL, NULL, NULL, NULL),
(89, 8, 6, 'Oral Paste Dietary Supplement', 'Oral paste, (triamcinolone acetonide cream), can get rid of mouth ulcers and denture sores in many cases with only a few applications.\r\n\r\n\r\n\r\nUnlike most gels available Trinolone Oral paste adheres to the surface of an ulcer or sore. and if applied early can prevent ulcers from developing or aid healing considerably.\r\n\r\n\r\n\r\n Trinolone paste also substantially reduces the painful symptoms of many oral complaints Including: Recurrent Ulcerative stomatitis, erosive lichen planus, denture stomatitis, traumatic lesions including denture spots, desquamative gingivitis, stomatitis and aphthous stomatitis.\r\n\r\n \r\n\r\nHow to Treat Mouth Ulcers with Trinolone triamcinolone acetonide cream\r\n\r\n \r\n\r\nApply to the affected area at bedtime. It may be necessary to apply 2-3 times a day, (preferably after meals), depending on severity of the symptoms.\r\n\r\n (Our personal recommendation; apply using a cotton bud, first dry the surface of the ulcer and then apply cream using the other end).', 25.00, 5, '/static/uploads/products/3a57764df60e44adb74567788f0424be_Screenshot_2025-11-24_105751.png', 'active', '2025-11-24 02:59:05', '2025-11-24 02:59:05', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'oral-paste-dietary-supplement', NULL, NULL, NULL, NULL),
(90, 8, 6, 'Dog & Cat Seaweed Lecithin Hair Care', '▶️Details:\r\n\r\n1. Egg yolk lecithin, help hair health: high purity, easy to absorb;\r\n\r\n2. Hair care and skin care: reduce hair loss, improve bright color, smooth hair, bioactive inositol;\r\n\r\n3. Reduce skin problems: dry skin, itching, dandruff, etc.;\r\n\r\n4. Regulate the stomach and improve the absorption of calcium and magnesium: rich in short-chain fructooligosaccharides, calcium hydrogen phosphate, and VD3 scientific ratio;\r\n\r\n5. Nutrition and health, reject preservatives, food attractants, curing agents, etc.;\r\n\r\n\r\n\r\n▶️Capacity: 300g\r\n\r\n▶️Shelf Life: 18 months\r\n\r\n\r\n\r\n▶️Main ingredients:\r\n\r\nChicken powder, chicken liver powder, brown rice flour, oat flour, \r\n\r\nSaccharomyces cerevisiae extract, egg yolk powder, chicken, water.\r\n\r\n\r\n\r\nLecithin, vitamin A, vitamin C, vitamin D3, vitamin E, niacinamide, D-calcium pantothenate, \r\n\r\nvitamin B1, vitamin B2, vitamin B6, vitamin B12, folic acid, D-biotin, etc.\r\n\r\n\r\n\r\n🔺How to use:\r\n\r\n✔️Daily supplementation\r\n\r\nFor Every 2kg of weight increase, add 1pcs per day\r\n\r\n(For example  2kg: 1pcs/day,   4kg: 2pcs/day,  6kg: 3pcs/day,   8kg: 4pcs/day...and so on)\r\n\r\n✔️Hair changing phase\r\n\r\nFor every 2kg of weight increase, add 1-2pcs per day\r\n\r\n(For example  2kg: 1pcs~2pcs/day,   4kg: 2pcs~4pcs/day,   \r\n\r\n6kg: 3~6pcs/day,  8kg: 4~8pcs/day...and so on)\r\n\r\n▶️Recommended for dogs over three months old\r\n\r\n\r\n\r\n--------------------------------------------------------------------\r\n\r\n🐶🐱Omega 3 Fish Oil for Dogs and Cats\r\n\r\n▶️Details：\r\n\r\n1.Supports the health of heart, joint, brain, skin and eyes\r\n\r\n2.Protects the liver and heart\r\n\r\n3.OMEGA-6 to 9 can help to enhance immunity and strengthen bones\r\n\r\n\r\n\r\nPuainta’s super concentrated fish oil is used to help relieve skin inflammation and reduce excessive hair loss (in dogs and cats), support the brain development, improve vision, nourish skin, encourage hair growth, enhance immunity, inhibit oxidation and aging, protect cardiovascular system, regulate blood lipid and help reduce risk of cardiovascular diseases.\r\n\r\n\r\n\r\n▶️Shelf Life: 24 months\r\n\r\n▶️Target Species: Dogs and cats.\r\n\r\n▶️Capacity: 0.45g*20pcs\r\n\r\n▶️Ingredients：\r\n\r\nConcentrated Anchovy Oil, Antarctic Krill Oil, Linseed Oil, etc.\r\n\r\n▶️Additives\r\n\r\nVitamin A and Vitamin E.\r\n\r\n\r\n\r\n▶️How to use:\r\n\r\n🐶Dog\r\n\r\n✅Small dog - Under 22 lbs (10 kg): 1-2 Capsules/day\r\n\r\n✅Medium dog - 22-55 lbs (10-25 kg): 1-2 Capsules/day\r\n\r\n✅Large dog - 55-88 lbs (25-40 kg): 2-3 Capsules/day\r\n\r\n🐈Cat\r\n\r\n✅Under 4.4 lbs (2 kg): 1 Capsule/2 days\r\n\r\n✅Over 4.4 lbs (2 kg): 1 Capsule/day\r\n\r\n\r\n\r\nDaily Feeding Amount: Please refer to the suggested dosagebased on dogs and cats of different sizes.\r\n\r\nIn case of impaired development, joint discomfort, pregnancy, etc., the amountmay be increased.\r\n\r\nlf two or more capsules are required daily,it is not recommended to give all the capsules at a time, butseparately.', 39.00, 43, '/static/uploads/products/998ebf6b0fca4cbea6a33810912e52e4_408d1b34-f681-4ec9-9614-93d2ead914b3.jpg', 'active', '2025-11-24 03:00:41', '2025-11-24 03:00:41', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'dog-cat-seaweed-lecithin-hair-care', NULL, NULL, NULL, NULL),
(91, 8, 6, 'Pet Deworming Tablet', 'Cats and dogs may require Dualmectin Dewormer Chewable Tablets  if they exhibit the following symptoms:\r\n\r\n\r\n\r\n1.Skin itching or rash: External parasites (such as fleas or ticks) can lead to skin allergies, rashes, itching, and constant scratching.\r\n\r\n2.Weight loss or emaciation: Internal parasites (such as roundworms or hookworms) can impair nutrient absorption, leading to weight loss or emaciation.\r\n\r\n3.Vomiting and diarrhea: Repeated vomiting or diarrhea may indicate internal parasitic infection, especially in cases of intestinal worms.\r\n\r\n4.Abnormal stool: The presence of small worms, blood, or mucus in stool can be a sign of parasitic infection.\r\n\r\n5.Frequent licking of the anus or anal itching: Parasites causing intestinal discomfort may lead pets to frequently lick or drag their anus, showing signs of itching or irritation.\r\n\r\n6.Swollen abdomen: Especially in young pets, a swollen or firm abdomen is commonly associated with internal parasites.\r\n\r\n7.Rough or shedding coat: Parasitic infections can cause a pet\'s coat to lose its shine, become coarse, and even lead to hair loss.\r\n\r\n8.Abnormal appetite: Infected pets may display excessive hunger without weight gain or lose their appetite completely.\r\n\r\n9.Frequent coughing: Certain parasites (such as hookworms or heartworms) may travel to the lungs, causing coughing or respiratory discomfort.\r\n\r\n\r\n\r\n🌼🌼🌼\r\n\r\nThe main functions of Dualmectin Dewormer Chewable Tablets for cats and dogs include:\r\n\r\n\r\n\r\n1.Broad-Spectrum Deworming Effect: Dualmectin contains dual-action deworming ingredients that effectively combat various internal and external parasites, including roundworms, hookworms, tapeworms, heartworms, as well as external parasites like fleas and ticks. This broad-spectrum deworming offers comprehensive protection for pet health.\r\n\r\n2.Alleviates Parasite-Induced Symptoms: By eliminating parasites, Dualmectin helps pets relieve discomfort associated with parasite infections, such as digestive issues, vomiting, diarrhea, weight loss, and rough fur.\r\n\r\n3.Reduces Risk of Reinfection: The deworming ingredients in Dualmectin act throughout the lifecycle of both internal and external parasites, helping pets build lasting protection and lowering the risk of reinfection.\r\n\r\n4.Improves Skin and Coat Health: By eliminating external parasites like fleas and ticks, Dualmectin reduces issues such as itching, skin allergies, and hair loss caused by these pests, helping pets maintain healthy skin and a shiny coat.\r\n\r\n5.Enhances Immunity and Overall Health: After parasite removal, pets’ nutrient absorption and digestive functions improve, boosting immunity and helping them maintain an ideal weight, ultimately enhancing overall health.\r\n\r\n6.Easy-to-Feed Chewable Tablets: Dualmectin Dewormer is designed as a chewable tablet with flavors that appeal to pets, making deworming easy and stress-free.\r\n\r\n\r\n\r\n🌼🌼🌼\r\n\r\nUsage and Dosage:\r\n\r\n-For Dogs：\r\n\r\n2kg-3.5kg，1pcs\r\n\r\n3.5kg-7.5kg，2pcs\r\n\r\n7.5kg-15kg，3pcs\r\n\r\n15kg-30kg，4pcs\r\n\r\n30kg-60kg，5pcs\r\n\r\nChoose the specifcations based on body weight, Each serving one, 7-10 days can be fed again.\r\n\r\n1. Puppies can be administered at 4 weeks of age, every three weeks a deworming until 12 weeks of age.\r\n\r\nThen every 3 months off 1 time.\r\n\r\n2. Adult dogs every 3 months a deworming.\r\n\r\n3. Dosing recommendations 1 hour before and after fasting.\r\n\r\n\r\n\r\n🌼🌼🌼\r\n\r\n-For Cats:\r\n\r\n0.5kg-1kg，1pcs\r\n\r\n1kg-2kg，2pcs\r\n\r\n2kg-4kg，3pcs\r\n\r\n4kg-8kg，4pcs\r\n\r\n8kg-12kg，5pcs\r\n\r\nChoose the specifcations based on body weight, Each serving one, 7-10 days can be fed again.\r\n\r\n1. Kitten: sixth, eighth, Twelfth weeks after the insecticide once every 3 months off once.\r\n\r\n2.Adult cats ( over 6 months ):every 3 months a worming.\r\n\r\n3. Dosing recommendations 1 hours before and after fasting.\r\n\r\n\r\n\r\n🌼🌼🌼\r\n\r\nCommon name: Dualmectin Dewormer Chewable Tablets for Cats & Dogs\r\n\r\nMain ingredient:\r\n\r\nEucalyptus Leaf Extract, Lavender Extract,Marigold Extract, Quisqualis Extract,Neem Bark Extract, Chicken, Corn Starch（For Dogs）\r\n\r\nEucalyptus Leaf Extract, Lavender Extract,.Atractylodes Powder Extract, QuisqualisExtract, Perilla Extract, Chicken, Corn Starch（For Cats）\r\n\r\nNet Weight:10 tablets/box\r\n\r\nFunction: Kills internal & external parasites\r\n\r\nShelf life: 24 months', 39.00, 51, '/static/uploads/products/ea76a46db91b453da24b81b6e8273a71_f7506a38-c63d-4823-aab0-0db21778c17b.jpg', 'active', '2025-11-24 03:02:26', '2025-11-26 05:31:49', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-deworming-tablet', NULL, NULL, NULL, NULL),
(92, 8, 6, 'Pet flea collar 8Months Lasting Protection Anti Insect Flea Tick Collar for Dog Cat', '🐶🐱Herbal Anti-Tick & Flea Collar for Dogs & Cats\r\n\r\nLong-Lasting Protection Against Ticks, Fleas & Mosquitoes—Safe for Your Furry Friend!\r\n\r\n🌟 5 Reasons Filipino Pet Parents Love This Collar\r\n\r\n✅ 1. 3-in-1 Pest Defense\r\n\r\nKills and repels the pests that trouble PH pets most:\r\n\r\n\r\n\r\nTicks (carriers of dengue and Lyme disease)\r\n\r\nFleas (cause itching, allergies, and anemia)\r\n\r\nMosquitoes (spread heartworm and other viruses)\r\n\r\nKeeps your pet protected whether they’re playing indoors or exploring your backyard.\r\n\r\n\r\n\r\n✅ 2. Fast-Acting & Long-Lasting\r\n\r\n\r\n\r\nStarts working within 24 hours of activation\r\n\r\nProvides 6 months of non-stop protection (no monthly reapplication like spot-ons)—saves you time and money.\r\n\r\n\r\n\r\n✅ 3. Natural Herbal Formula (Pet & Eco-Friendly)\r\n\r\nCoated with 7 safe, plant-based oils:\r\n\r\n\r\n\r\nCatnip Oil (repels fleas), Geranium Oil (fights ticks), Lavender True Oil (soothes skin)\r\n\r\nClary Sage Oil, Cedrus Atlantica Oil, Niaouli Oil, Patchouli Oil (boosts pest defense)\r\n\r\nNo harsh chemicals (like permethrin) that irritate sensitive skin—safe for puppies/kittens over 2 months old.\r\n\r\n\r\n\r\n✅ 4. Perfect Fit for Every Pet\r\n\r\n\r\n\r\nDog Collar: 60cm length (fits small to large breeds—Chihuahua to Golden Retriever)\r\n\r\nCat Collar: 33cm length (ideal for all cat breeds—Siamese to Maine Coon)\r\n\r\nAdjustable buckle design ensures a comfy fit (2 fingers should slide between collar and skin).\r\n\r\n\r\n\r\n✅ 5. Durable & Easy to Use\r\n\r\n\r\n\r\n100% polyester ribbon resists tearing, water, and dirt—stays effective even after baths or rain.\r\n\r\nSimple activation: Just stretch, buckle, trim excess, and go!\r\n\r\n\r\n\r\n▶️Capacity:  Dog 60cm;   Cat  33cm\r\n\r\n▶️Color: Orange/Grey\r\n\r\n▶️Shelf Life: 2 years\r\n\r\n▶️Active Ingredients:\r\n\r\nFormula Coating : Catnip Oil, Geranium Oil, Lavender True Oil,\r\n\r\nClary Sage Oil, Cedrus Atlantica Oil, Niaouli Oil, Patchouli\r\n\r\nOil-3%, PVC Compound-97%\r\n\r\nPattern Ribbon :Polyester-100%\r\n\r\n\r\n\r\n▶️How to use\r\n\r\n1. After stretching to activate, place the collar around the\r\n\r\ndog or cat\'s neck and buckle in place.\r\n\r\n2. Make sure two fingers fit snugly between the collar\r\n\r\nand your dog\'s skin, and adjust to the correct length.\r\n\r\n3. Leave 2 or 3 inches of collar behind the buttons for\r\n\r\nadditional adjustments, then cut off at the appropriate length.\r\n\r\n\r\n\r\n▶️Attention: \r\n\r\nIf you use the anti tick and flea tube for your dog/cat, \r\n\r\nIt is better to use this anti flea tick collar after 3-7 days.', 39.00, 5, '/static/uploads/products/18fd1fa2cc8f4a73b0f53aaffea1ce81_2ea62138-e6e1-4563-8dd2-8e4a530e4995.jpg', 'active', '2025-11-24 03:04:21', '2025-11-24 08:25:21', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-flea-collar-8months-lasting-protection-anti-insect-flea-tick-collar-for-dog-cat', NULL, NULL, NULL, NULL),
(93, 8, 6, 'Pet ear mites cleaner odor Removal Ear Drops 60ml Eye drops Infection Solution Treatment Cleaner', '▶️Details:\r\n\r\n1.Clean the earwax and dead cutin\r\n\r\n2.Helps shrink skin pores, revitalize skin, antibacterial, anti-inflammatory and skin allergy inhibition\r\n\r\n3.Gently soothes sensitive skin, helps skin repair and wound healing\r\n\r\n4.Helps enhance skin activity, helps kill scabs, and eliminate inflammation\r\n\r\n\r\n\r\n\r\n\r\n▶️Shelf life: 24 months\r\n\r\n▶️Capacity: 60ml\r\n\r\n\r\n\r\n▶️Ingredients:\r\n\r\nChrysanthemum Oil, Witch Hazel Extract, Calendula Flower Oil, EDTA, \r\n\r\nTromethamine, Sodium Diethylhexyl Sulfosuccinate, Propylene Glycol, Purified Water.\r\n\r\n\r\n\r\n▶️How to use\r\n\r\nShake gently, twist 1-2 turns, squeeze out the solution.\r\n\r\n①Drop the appropriate amount of ear drops.\r\n\r\n3-4drops once time. Use 2-3 times a day.\r\n\r\n②Gently massage the base of the ear for 20seconds\r\n\r\n③Wipe off the dirt with tissue cottoncloth\r\n\r\nEar problem Treatment:  Continue using for 5-7 days\r\n\r\n\r\n\r\nIf you use it for daily ear cleaning for your pets, 2-3 times a week\r\n\r\n\r\n\r\n▶️Attention: \r\n\r\n1. Do not pour a large amount of ear care solution into the ear.\r\n\r\n2. Keep it out of reach of children.\r\n\r\n3.We are updating the package of the ear cleaning drops. The new and old package are sent out randomly.', 39.00, 5, '/static/uploads/products/8674f23a809b4be6ab76ee6a4ab1a88e_8632d784-bac6-4b2a-aa15-913043297b20.jpg', 'active', '2025-11-24 03:06:06', '2025-11-26 04:44:56', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-ear-mites-cleaner-odor-removal-ear-drops-60ml-eye-drops-infection-solution-treatment-cleaner', NULL, NULL, NULL, NULL);
INSERT INTO `products` (`id`, `seller_id`, `category_id`, `name`, `description`, `price`, `stock_quantity`, `image_url`, `status`, `created_at`, `updated_at`, `sku`, `weight`, `dimensions`, `brand`, `age_group`, `pet_type`, `featured`, `seller_latitude`, `seller_longitude`, `low_stock_threshold`, `meta_title`, `meta_description`, `meta_keywords`, `slug`, `sale_price`, `sale_start_date`, `sale_end_date`, `cost_price`) VALUES
(94, 8, 6, 'Pet Dental Wipes for Dog cat Remove Pet oral cleaning supply', 'What symptoms do pets need to use finger wipes for?\r\n\r\n1. Oral odor: If a pet\'s mouth has an odor, it may be caused by food residue, tartar, or tartar. At this point, you can use oral wipes to gently wipe your pet\'s tongue, teeth, and gums, which can help remove odors and maintain oral hygiene.\r\n\r\n2. Accumulation of dental plaque: Pet teeth are prone to accumulating dental plaque, which can lead to problems such as bad breath and tartar if left uncleaned for a long time. Regular use of oral wipes for wiping can effectively prevent the accumulation of dental plaque.\r\n\r\n3. Increased drooling: If a pet drowns more, it may be caused by oral infections, dental calculus, or other reasons. Using oral wipes to wipe can help clean saliva, while observing the pet\'s oral condition. If there are any abnormalities, seek medical attention promptly.\r\n\r\n4. Oral ulcers or inflammation: If a pet develops oral ulcers or inflammation, oral wipes can be used to wipe and clean the ulcer area, but care should be taken to avoid excessive force to avoid worsening the symptoms.\r\n\r\n\r\n\r\n🌼🌼🌼\r\n\r\nName : Pet Teeth Cleaning Finger Wipes\r\n\r\nQuantity : 50 pcs\r\n\r\nSuitable : Dogs & Cats\r\n\r\nShelf Life : 24 months\r\n\r\nEfficacy : Pet Dental Plaque, Eye Discharge, Nasal Dirt and other local stain\r\n\r\nIngedients : Deionized Water，HP100 Antibacterial Agent, PropyleneGlycol, Cationic surfactant, Lysozyme,High-QualityNon-woven Fabric, etc.', 36.00, 54, '/static/uploads/products/952ec424744b4d259560daa962f391e8_3bf87d70-02f0-4b0e-9491-4aba855927dc.jpg', 'active', '2025-11-24 03:07:39', '2025-11-26 13:31:22', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'pet-dental-wipes-for-dog-cat-remove-pet-oral-cleaning-supply', NULL, NULL, NULL, NULL),
(95, 8, 6, 'Dog and cat shampoo flea and tick shampoo 500ML', 'flea and tick pet shampoo conditions and deodorizes pet\'s coat. It is hypoallergenic and paraben-free that keeps your pet safe during bath time. It contains an all in one formula which makes bath time easy for you and your pet whilst killing all your pet\'s enemies. It also prevents flea eggs from hatching for up to 28days.', 39.00, 4, '/static/uploads/products/e7eb680208c14251b3e28b88a4e4c39b_be1be783-a4a9-4c45-a9a6-84f33a969ae6.jpg', 'active', '2025-11-24 03:09:41', '2025-11-25 16:00:44', NULL, NULL, NULL, NULL, 'all_ages', 'dog', 0, 14.59950000, 120.98420000, 10, NULL, NULL, NULL, 'dog-and-cat-shampoo-flea-and-tick-shampoo-500ml', NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `product_bundles`
--

CREATE TABLE `product_bundles` (
  `id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `bundle_price` decimal(10,2) NOT NULL,
  `discount_percentage` decimal(5,2) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `product_images`
--

CREATE TABLE `product_images` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `display_order` int(11) DEFAULT 0,
  `is_primary` tinyint(1) DEFAULT NULL,
  `alt_text` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `product_images`
--

INSERT INTO `product_images` (`id`, `product_id`, `image_url`, `display_order`, `is_primary`, `alt_text`, `created_at`) VALUES
(1, 7, '/static/uploads/products/8f8bd4f902484b0bbd90656bc0bf62d2_rui_on_Instagram____1_D299_....jpg', 0, 1, NULL, NULL),
(4, 19, '/static/uploads/products/1e7ab217ca034cfea40e2b0f3fb5488a_4065271d09612558a2589304cbe9bf75.jpg', 0, 1, NULL, NULL),
(5, 19, '/static/uploads/products/88467bfea0fd438cafd797296440119c_d3281ba720a0aaff0d0f72e9a0e594be.jpg', 1, 0, NULL, NULL),
(6, 19, '/static/uploads/products/97333703f7d447d2b61434fc67175bb4_8ed4dc806172d1a99f88e6ecd09852e4.jpg', 2, 0, NULL, NULL),
(7, 20, '/static/uploads/products/3f60ac94f4324809b15a5896c86ce658_BLACK.jpg', 0, 1, NULL, NULL),
(8, 20, '/static/uploads/products/d60364c656684d63bc29d3bb50df161f_GREEN.jpg', 1, 0, NULL, NULL),
(9, 20, '/static/uploads/products/982a1ea101b44ccabf7d40c187bc003e_PINK.jpg', 2, 0, NULL, NULL),
(10, 20, '/static/uploads/products/7903e4e5a7db44ddba00f102b4fa06a7_PURPLE.jpg', 3, 0, NULL, NULL),
(11, 20, '/static/uploads/products/31744afa29a348858324652879580c12_BLUE.jpg', 4, 0, NULL, NULL),
(12, 20, '/static/uploads/products/80430aeebc9d4d778c83147082231765_RED.jpg', 5, 0, NULL, NULL),
(13, 23, '/static/uploads/products/8c6a263b946a4a9b9bbea5887a47d818_RED_1.jpg', 0, 1, NULL, NULL),
(14, 23, '/static/uploads/products/c7a6ee726f814654a9ece030a2e9ae77_GREEN_1.jpg', 1, 0, NULL, NULL),
(15, 23, '/static/uploads/products/17868d12f9dd4796a56f1e4753bae3ca_105e64f58f83b0e7fa154a0621d5553a.jpg', 2, 0, NULL, NULL),
(16, 23, '/static/uploads/products/c0ed0ce6042f43218e8e29c2bca9ee8f_BLUE_1.jpg', 3, 0, NULL, NULL),
(17, 24, '/static/uploads/products/48ad3e2085d54762b93985de85e10737_debe07ce01e51a77c18cbcc68a695caa.jpg', 0, 1, NULL, NULL),
(18, 24, '/static/uploads/products/69dbf24ce01746a29b0c273c76489375_CAT_MOUSE.jpg', 1, 0, NULL, NULL),
(19, 24, '/static/uploads/products/66c826fce4814b19b13e623453ba7ea7_6e122814387e00622bdd64168db7448f.jpg', 2, 0, NULL, NULL),
(20, 24, '/static/uploads/products/eff75a126e8f4f7ab02765cc36f6eb37_4ac457f6f1bfc017c48db26ecb0d1c01.jpg', 3, 0, NULL, NULL),
(21, 25, '/static/uploads/products/9f2bae9c6d85418091c98bfd7e5d0a7c_sg-11134201-22110-hl6kvf1jvdkv1a.jpg', 0, 1, NULL, NULL),
(22, 25, '/static/uploads/products/94cfa63c61e84de5945f646492f64127_sg-11134201-22110-khq3nk6jvdkvc3.jpg', 1, 0, NULL, NULL),
(23, 25, '/static/uploads/products/23bfbf6cefb844f383a96d8d0b69486a_CAT_SCRATCHES.jpg', 2, 0, NULL, NULL),
(24, 25, '/static/uploads/products/cca1bf39c8f74deb91bc581391a797f1_3a19f718574e60b54d691f0da8aa719c.jpg', 3, 0, NULL, NULL),
(25, 26, '/static/uploads/products/03430c2bc84e4e799451a371bc390180_47b754e5bb29a18c7d2e1b83e610e831.jpg', 0, 1, NULL, NULL),
(26, 26, '/static/uploads/products/45be54b5a6ee47e5916a3e165e8d7ded_BLACK.jpg', 1, 0, NULL, NULL),
(27, 26, '/static/uploads/products/d2c54376376347e7a2ca353fe1231ba2_BLUE.jpg', 2, 0, NULL, NULL),
(28, 26, '/static/uploads/products/2eec4e7b110a429dac05cdd5d3b4efc6_DARK_GREEN.jpg', 3, 0, NULL, NULL),
(29, 26, '/static/uploads/products/0e3ed52ba9804a9da503eae9cbb17161_PURPLE.jpg', 4, 0, NULL, NULL),
(36, 30, '/static/uploads/products/04ccf1f632204624a0fe84852628d928_0ea1b6cb-f834-49e1-ad3e-250387993a6b.jpg', 0, 1, NULL, NULL),
(37, 30, '/static/uploads/products/80f85376c5ff405c9eaf3da07313c055_062d6c6d-2950-4e90-b141-9c5cc80749e6.jpg', 1, 0, NULL, NULL),
(38, 30, '/static/uploads/products/e16681a7dcf142d9812bbcb9f38edba4_bc8dae0a-c121-448b-8e07-3a2b5b200927.jpg', 2, 0, NULL, NULL),
(39, 30, '/static/uploads/products/3208cd1093ab4bf5a4f3ffcde52c778f_a28d73b2-d0ed-4a9d-9ea8-b5bfb73d564f.jpg', 3, 0, NULL, NULL),
(40, 30, '/static/uploads/products/17145cde4db34b5fa65d1f71a55c68c9_64a70d4e-d994-4263-aab1-9524eacc08c5.jpg', 4, 0, NULL, NULL),
(41, 30, '/static/uploads/products/8b86109525be4bcca72e3fa6cd15e565_5a27360b-a666-4790-9d1c-a09083330ef5.jpg', 5, 0, NULL, NULL),
(42, 30, '/static/uploads/products/cbbe3e3272984acbbb9d2e162b48eed0_772cc039-c9cb-49df-b102-b4b1cb5405b8.jpg', 6, 0, NULL, NULL),
(43, 30, '/static/uploads/products/9a01bf18c52d479cbc2db6536427d453_9457335f-bb22-4cee-b039-6f922a554a66.jpg', 7, 0, NULL, NULL),
(44, 30, '/static/uploads/products/f472c80194744ad983148379b8dfd8c5_4072ef2c-36e0-49c9-bbef-4df123c479fe.jpg', 8, 0, NULL, NULL),
(45, 31, '/static/uploads/products/1dd2b6f8104d454fa0a0d72dbd488536_ce5163d7-9205-471d-95a7-1203c4036aea.jpg', 0, 1, NULL, NULL),
(46, 31, '/static/uploads/products/52605944693d4dceb38a4bd517f71028_2ed65ea6-02f7-412b-8a89-53e98c94fc5e.jpg', 1, 0, NULL, NULL),
(47, 31, '/static/uploads/products/ecfca012826f4c73b7527516bd3ce4c0_ffb92133-c0bf-4f1a-8622-86e389c94ee3.jpg', 2, 0, NULL, NULL),
(48, 31, '/static/uploads/products/08f10d5120ea4869b229db609cfb17bc_a6121dd8-e51f-4d71-9c9d-2bf3653ed040.jpg', 3, 0, NULL, NULL),
(49, 31, '/static/uploads/products/e471874f576b49ebbbe79078bdb16b68_9949707e-e496-4ff9-bf84-b6f32a6482a6.jpg', 4, 0, NULL, NULL),
(50, 31, '/static/uploads/products/753f66851eaf4844a8d18681fe81e811_55bd7539-75b6-4b00-b4a2-e64789ab1e4c.jpg', 5, 0, NULL, NULL),
(51, 31, '/static/uploads/products/40178893d8214dc58b886717e7989cd0_69e0c016-2cd0-4913-bbf7-ee6cc8392af7.jpg', 6, 0, NULL, NULL),
(61, 32, '/static/uploads/products/c7b3d42b9df04954bc3af981426a0c44_a653e3d4-a366-4fc2-bf5f-0efd52f2f446.jpg', 0, 1, NULL, NULL),
(62, 32, '/static/uploads/products/b676b30f2c1141ef86eae94abc535866_643d3b77-deea-4b9a-bcc7-b92d24cb8795.jpg', 1, 0, NULL, NULL),
(63, 32, '/static/uploads/products/47c56fb6472847618cc651b28896876f_8d498e29-a018-4cc7-a19b-37ad49d93c2e.jpg', 2, 0, NULL, NULL),
(64, 32, '/static/uploads/products/f6ddceac65ea49e9ba4768664f0b1c2b_94d2f10a-e8cd-4ec0-99d3-fbff317ce259.jpg', 3, 0, NULL, NULL),
(65, 32, '/static/uploads/products/76d24ae35ae54c2cae8491b1791d6481_c89e8b62-bfe4-4f33-8098-2d71057c2909.jpg', 4, 0, NULL, NULL),
(66, 32, '/static/uploads/products/3ad55bbcfcca477eb09e72708292dc87_a472e638-058f-4545-8840-e433a81a0f9e.jpg', 5, 0, NULL, NULL),
(67, 32, '/static/uploads/products/2e491318471843219321647a980dd801_87cada32-e6d5-43a1-a19a-f166d9a4cc2f.jpg', 6, 0, NULL, NULL),
(68, 32, '/static/uploads/products/3fa6bcfb08404148b2a509b385165d6b_e2fb32ea-6439-4a15-a2d6-2fffb4601a1b.jpg', 7, 0, NULL, NULL),
(69, 32, '/static/uploads/products/cb7e7527a3e64706bd87afafad668ce5_7bc69cc3-1e8a-4b41-a938-21a41021363d.jpg', 8, 0, NULL, NULL),
(70, 33, '/static/uploads/products/1387886d9fe94c369653f49f0fd149fe_c5d3e885-dfa5-49f2-928d-8d45f9d13115.jpg', 0, 1, NULL, NULL),
(71, 33, '/static/uploads/products/40edb2c730404ea3a1a4c02177300707_8d498e29-a018-4cc7-a19b-37ad49d93c2e.jpg', 1, 0, NULL, NULL),
(72, 33, '/static/uploads/products/a0adf38b5079496c9ce0fe7b231ea92b_94d2f10a-e8cd-4ec0-99d3-fbff317ce259.jpg', 2, 0, NULL, NULL),
(73, 33, '/static/uploads/products/ea771b60a8b94ee7aa4028474545648c_c89e8b62-bfe4-4f33-8098-2d71057c2909.jpg', 3, 0, NULL, NULL),
(74, 33, '/static/uploads/products/29aa85e7cac84985a5381264e0db973e_a472e638-058f-4545-8840-e433a81a0f9e.jpg', 4, 0, NULL, NULL),
(75, 33, '/static/uploads/products/e12852042c3b4a4fa29d8d0d9cf5c420_87cada32-e6d5-43a1-a19a-f166d9a4cc2f.jpg', 5, 0, NULL, NULL),
(76, 33, '/static/uploads/products/d6766b4f6e4240f7900b17698e68696e_e2fb32ea-6439-4a15-a2d6-2fffb4601a1b.jpg', 6, 0, NULL, NULL),
(77, 33, '/static/uploads/products/ce4b90e784ed4d27bef0640bebbacf44_6b4bb043-9610-4942-94f3-b58b43d04368.jpg', 7, 0, NULL, NULL),
(78, 33, '/static/uploads/products/00398e8b5b87496db8d3f3a15afed197_93444501-a625-48ce-8419-22f297dbd97f.jpg', 8, 0, NULL, NULL),
(79, 34, '/static/uploads/products/64caf4473cfa45f18624da8b1633fabb_e449285a-5108-4f72-bb80-1ed9be0448f6.jpg', 0, 1, NULL, NULL),
(80, 34, '/static/uploads/products/1760ce673d30439aa4848633f5b3a8ed_dcf611d0-9de3-4866-8d40-3f4e6a964b83.jpg', 1, 0, NULL, NULL),
(81, 34, '/static/uploads/products/e3ebe8e6fc8a41e9b4212a68ab911ede_f8a2c1f5-c91f-40f3-b2b2-86e1b9319886.jpg', 2, 0, NULL, NULL),
(82, 34, '/static/uploads/products/e14470e0dbd84e64aa48e88a5e99d537_026831c1-ce6b-444e-917c-b369f729668a.jpg', 3, 0, NULL, NULL),
(83, 34, '/static/uploads/products/849972a62eba49b09962e30e6bc38b30_996eb0e7-891b-4e22-a3a1-ea2fe7ae3b45.jpg', 4, 0, NULL, NULL),
(84, 34, '/static/uploads/products/43de682b7f0e4630ae44ff4a8c12b8f1_a4803bcb-355f-4537-b3e6-2d0929c4f23d.jpg', 5, 0, NULL, NULL),
(85, 34, '/static/uploads/products/10432055a34746ae9bcbd788922c6d9d_9d525c73-8e3e-4580-a692-18cb92785e9b.jpg', 6, 0, NULL, NULL),
(86, 34, '/static/uploads/products/0793b20a37c245159127763a17d80ea1_779cec1f-7d83-4c8b-baee-dd3efeb10020.jpg', 7, 0, NULL, NULL),
(87, 34, '/static/uploads/products/178a5d6a9e0a499cb32f09922f999f6d_9509f008-0c2b-43cb-a944-88c72a1c2e71.jpg', 8, 0, NULL, NULL),
(88, 35, '/static/uploads/products/568e10f8ea144b938c6fbddaefe13b2e_e449285a-5108-4f72-bb80-1ed9be0448f6.jpg', 0, 1, NULL, NULL),
(89, 35, '/static/uploads/products/fae44b58ac4b4d3e9dde791510701bbc_291ef15b-9154-4ea2-b4be-4c016862f446.jpg', 1, 0, NULL, NULL),
(90, 35, '/static/uploads/products/bfc384c47f2f45499cab1c8efaf178e7_981a32c3-578f-4d69-95dc-e11ecf274d83.jpg', 2, 0, NULL, NULL),
(91, 35, '/static/uploads/products/bddc69a710e540a6a4b06f520cfa1adc_e4d027e7-9a27-4ca8-9c83-da29eabdcf1e.jpg', 3, 0, NULL, NULL),
(92, 35, '/static/uploads/products/0a88bb79012046708750c6f71e55da65_be3c6c46-3ef7-4b12-ac56-f38492ef0d60.jpg', 4, 0, NULL, NULL),
(93, 35, '/static/uploads/products/9fefaafb2dac41169e705f872bf9ef91_ac3ce98f-736a-4a1d-99c8-c2042ee03329.jpg', 5, 0, NULL, NULL),
(94, 35, '/static/uploads/products/1be571dd6bf54b7fa3127fbcedeea19a_3d288419-7029-49a0-822f-76a655f5fe5b.jpg', 6, 0, NULL, NULL),
(95, 35, '/static/uploads/products/0d1ec32d05c0496d95e0a317684fa698_edb846fb-12ed-41a7-992b-002830aa7f06.jpg', 7, 0, NULL, NULL),
(96, 35, '/static/uploads/products/27598dfb253f4fffa82c80ac7790c88e_fe10f2af-9b26-437b-a2c1-47eeff99bb97.jpg', 8, 0, NULL, NULL),
(97, 36, '/static/uploads/products/946c50d20d494dd7b030dfc8acdafc80_a9f704e5-5107-48a6-9b9d-6891243a230d.jpg', 0, 1, NULL, NULL),
(98, 36, '/static/uploads/products/cc8f5ea9433644018f805f560ae9c9dc_e4491f14-94db-475d-b344-a91adda57ea4.jpg', 1, 0, NULL, NULL),
(99, 36, '/static/uploads/products/2eb334ce5fad4d9fb1548ec4f5edefb9_496088a3-7158-46bc-b63b-972d79f752f2.jpg', 2, 0, NULL, NULL),
(100, 36, '/static/uploads/products/53e1f8ddaeb6481c95b705ac1b648a5f_414dd36e-be52-4069-90a4-8373a8a11631.jpg', 3, 0, NULL, NULL),
(101, 36, '/static/uploads/products/509fa79a54264bda91ca0f8ce9862588_89a66cc3-8e60-47cf-8378-eddb2bcaa6f8.jpg', 4, 0, NULL, NULL),
(102, 36, '/static/uploads/products/7f1695beeec948129cb0beaef5dfbec6_ca7c707b-6806-4864-9208-14e49669a1ae.jpg', 5, 0, NULL, NULL),
(103, 36, '/static/uploads/products/6299282360844255838caaf71a414058_f12d9724-0e24-47c3-8a85-5235cdaf020c.jpg', 6, 0, NULL, NULL),
(104, 36, '/static/uploads/products/6f450152cb2e4901bc3a6387aac22f30_8da3b9e9-7627-4d4f-a43d-3de929821cc9.jpg', 7, 0, NULL, NULL),
(105, 36, '/static/uploads/products/d9d3baa17a7440729a3475559b1c3132_12d82cc4-f168-4e46-8b16-caace2ba13a5.jpg', 8, 0, NULL, NULL),
(106, 37, '/static/uploads/products/29c173aabd1247128faf5e11f08950b9_3e44fef2-b3be-4a6c-9732-55ee02e8c912.jpg', 0, 1, NULL, NULL),
(107, 37, '/static/uploads/products/1e2a2acc988740999d7b5823e7480299_44ad6e54-3ef8-4686-97a4-a66343be13fd.jpg', 1, 0, NULL, NULL),
(108, 37, '/static/uploads/products/ca18cb84a73d41a499c8832e11a0456f_4f8c3afa-bc16-4edd-bd94-9ee1629609c2.jpg', 2, 0, NULL, NULL),
(109, 37, '/static/uploads/products/c87521a2011849ca814aea8f8df719b4_6d11babe-57e1-482e-b34e-3a9176a73037.jpg', 3, 0, NULL, NULL),
(110, 37, '/static/uploads/products/b120faef773d4072880fd8dad17e1994_c054f6eb-3566-424c-aa61-f6d69486a040.jpg', 4, 0, NULL, NULL),
(111, 37, '/static/uploads/products/de0da726cc9f4f7d853294db0718119d_ff2e36f0-12b6-42f6-bb02-979bda85f35b.jpg', 5, 0, NULL, NULL),
(112, 37, '/static/uploads/products/3f532e36e13f4daeb40e1a84697a2a9b_4f7e93d6-aabf-4e6d-910a-fb4507be7d9c.jpg', 6, 0, NULL, NULL),
(113, 37, '/static/uploads/products/b76dd8d417904f8ea7f5d0da67c374db_f18141d2-0335-419b-8185-1743a4906683.jpg', 7, 0, NULL, NULL),
(114, 37, '/static/uploads/products/6908857332444221a11c8011cb93cacf_18eaebad-7062-42d9-98c2-b2bb6748311d.jpg', 8, 0, NULL, NULL),
(115, 38, '/static/uploads/products/3bd59f0cd861468c902c0e027b844d26_b56d45f1-5d93-4e51-900f-d8319a8ea8df.jpg', 0, 1, NULL, NULL),
(116, 38, '/static/uploads/products/0cedd74b8848425d8ffabc928af0d51e_21adf3d6-d5c3-42c6-9b89-c016d8473f6b.jpg', 1, 0, NULL, NULL),
(117, 38, '/static/uploads/products/fb90e51b738f422aa9f1b06310f83d07_191f0d67-1da7-4138-8986-c0a6f65c4819.jpg', 2, 0, NULL, NULL),
(118, 38, '/static/uploads/products/6573fd973d894d00957a8ceae219f946_520de497-aebe-4d66-9a82-6fa84f9d2a5a.jpg', 3, 0, NULL, NULL),
(119, 38, '/static/uploads/products/d9535b5ccb8949e098e8e1b35dddd73d_c4933151-af33-40b6-8fd7-1e4fa31d98b9.jpg', 4, 0, NULL, NULL),
(120, 38, '/static/uploads/products/f75386cdfd1744fa8de274506667ab98_61dea2c6-ee23-43da-af6f-da83796e5f7f.jpg', 5, 0, NULL, NULL),
(121, 38, '/static/uploads/products/3b818745c63e499e9bb607714555ce26_f366a559-950b-404d-aaa3-6422b531de53.jpg', 6, 0, NULL, NULL),
(122, 38, '/static/uploads/products/b6332facf387480c9f6d2d3437387921_bbcc20de-21ed-4a8b-bb83-7392497bff1d.jpg', 7, 0, NULL, NULL),
(123, 39, '/static/uploads/products/d04f4520ba21482a8f44e257b5a448b2_783c20c5-a8fc-4adb-9562-acea1c9d7667.jpg', 0, 1, NULL, NULL),
(124, 39, '/static/uploads/products/bcdf0f81ddf94956951bcca11e01c1d6_a4233da7-5a4c-4f1c-8422-b15a1cda961e.jpg', 1, 0, NULL, NULL),
(125, 39, '/static/uploads/products/02d59c0937574b13bc68a11c9a873f61_fd5d7c4f-5054-4bf0-9c79-d8b74d4e9e2d.jpg', 2, 0, NULL, NULL),
(126, 39, '/static/uploads/products/c6a37defc32d49d88432853e9b6e4ae9_b08cc4da-06eb-4b8c-afc0-f363d148ea40.jpg', 3, 0, NULL, NULL),
(127, 39, '/static/uploads/products/f5e8c058bebf40b4a6b99482eb1cf468_7df4bede-15ce-467e-8d87-8a887c11ab77.jpg', 4, 0, NULL, NULL),
(128, 40, '/static/uploads/products/028c4cfa80724871a4917dac419e079c_b782ee43-9929-4e86-a27a-7386b4397b3c.jpg', 0, 1, NULL, NULL),
(129, 40, '/static/uploads/products/c369b1e1233a42fea380d9e93e9921dd_7cdce2c9-7f4b-4032-8d6e-16dd1dc524f1.jpg', 1, 0, NULL, NULL),
(130, 40, '/static/uploads/products/5de7cb3170844ccdb6985d41163f7c37_189e49b8-39ae-472e-936b-517950a4dd75.jpg', 2, 0, NULL, NULL),
(131, 41, '/static/uploads/products/16c20171ad524bbab758f0be8416d19a_9378d48a-5bc1-47eb-96f2-394cce6b1588.jpg', 0, 1, NULL, NULL),
(132, 41, '/static/uploads/products/760e1b781b7242e38007ad39f103c201_b88379b6-77a0-493d-9f15-cae87f22b10c.jpg', 1, 0, NULL, NULL),
(133, 41, '/static/uploads/products/5601ad735c3045edbb109627f85a855a_7559acf3-40ef-4ec6-abfc-633790f59bff.jpg', 2, 0, NULL, NULL),
(134, 41, '/static/uploads/products/1abe46fcdef841b48383eb2d8bc6125c_21adf3d6-d5c3-42c6-9b89-c016d8473f6b.jpg', 3, 0, NULL, NULL),
(135, 41, '/static/uploads/products/bc396116641e4efc8dd9600d438c96ed_520de497-aebe-4d66-9a82-6fa84f9d2a5a.jpg', 4, 0, NULL, NULL),
(136, 41, '/static/uploads/products/333cc79d33af41f7a91fa92a8970a867_b2b8ca66-23f1-464e-b1a0-73db404996fc.jpg', 5, 0, NULL, NULL),
(137, 41, '/static/uploads/products/702a25f72d754dc1856a4d05a6838e6e_20cb62b2-2e0a-4ad5-b1d3-cd4b9c2fd9c9.jpg', 6, 0, NULL, NULL),
(138, 42, '/static/uploads/products/35fb399f0f87460a9a3e9c9f8a6516a2_2bd6fba8-c13b-4081-a60d-035c320a4ab1.jpg', 0, 1, NULL, NULL),
(139, 42, '/static/uploads/products/42fa88d2d08849a19de97bcafbb843da_eff8f8ba-d243-4d41-a859-b3fc943dea82.jpg', 1, 0, NULL, NULL),
(140, 42, '/static/uploads/products/62b4b02abdfa4812a8f05e94ff6dd547_e6942e2a-96d9-46df-87bd-b56d164825e9.jpg', 2, 0, NULL, NULL),
(141, 42, '/static/uploads/products/b5cf2feedcaf449d82ce30a9cc4d9efa_17baf663-57d9-4e5e-8501-0992f1b61a64.jpg', 3, 0, NULL, NULL),
(142, 42, '/static/uploads/products/0cde042b366e4c66a959ae73edb0188e_0a185d07-8fe7-4fac-8edb-e274817af9a9.jpg', 4, 0, NULL, NULL),
(143, 42, '/static/uploads/products/6996261a39ae44d4af25fef2eba76b39_47034909-920c-4546-837f-0ff13b357ef6.jpg', 5, 0, NULL, NULL),
(144, 42, '/static/uploads/products/54ad7e19dd7c4be7beee5d80ec01ec5e_e2e3fb54-0714-463b-9b98-cf8db1580357.jpg', 6, 0, NULL, NULL),
(145, 43, '/static/uploads/products/7e4fd25c1bc14d8b98670d117060e064_cb5ff617-9703-41e2-b041-aa5ce7f10a22.jpg', 0, 1, NULL, NULL),
(146, 43, '/static/uploads/products/bc6c7fa90f884e5fbe7e7ad1d430d224_6206856d-36bf-48db-b396-3a89d0ebc8b3.jpg', 1, 0, NULL, NULL),
(147, 43, '/static/uploads/products/b79a6bd1e2ac432cb0091381a9b7a4ba_d024e980-6eec-4d1c-92f6-03fadb575a1b.jpg', 2, 0, NULL, NULL),
(148, 43, '/static/uploads/products/cf2267410b894d659b62288103de3f94_faf61422-79b5-499d-ba81-8c7b2dca900e.jpg', 3, 0, NULL, NULL),
(149, 44, '/static/uploads/products/b380f10dd5e04f6d8620dc33d22a6b94_cb5ff617-9703-41e2-b041-aa5ce7f10a22.jpg', 0, 1, NULL, NULL),
(150, 44, '/static/uploads/products/100e1ffd10524597942939202306febe_6206856d-36bf-48db-b396-3a89d0ebc8b3.jpg', 1, 0, NULL, NULL),
(151, 44, '/static/uploads/products/c70c9958c5884dcdab23fee5556bc157_d024e980-6eec-4d1c-92f6-03fadb575a1b.jpg', 2, 0, NULL, NULL),
(152, 44, '/static/uploads/products/6d2bd9f3d5c44060a8532a8a06752b16_faf61422-79b5-499d-ba81-8c7b2dca900e.jpg', 3, 0, NULL, NULL),
(153, 45, '/static/uploads/products/ad2a037607b5434881a96bf2b96c07aa_2c0ceba8-ce1a-4672-8640-b09d8dc43d86.jpg', 0, 1, NULL, NULL),
(154, 45, '/static/uploads/products/c1f694f8375b45f784c7dff48b0dc15c_cd02438a-6bbd-4581-b05e-f4dbd823fc07.jpg', 1, 0, NULL, NULL),
(155, 45, '/static/uploads/products/88532a07175b44709179ce463ee06ecf_6ef909c7-9825-423d-bb47-0c9374ba2dde.jpg', 2, 0, NULL, NULL),
(156, 45, '/static/uploads/products/6483cf0ca08d45d38d139b82d6c5afcc_b8949214-f0f0-49e0-ad10-c8aa66ec4573.jpg', 3, 0, NULL, NULL),
(157, 45, '/static/uploads/products/90690f6904c842979b2037f57a76b2e0_7aa65136-a47e-46ae-9ecc-d99f9fe08327.jpg', 4, 0, NULL, NULL),
(158, 45, '/static/uploads/products/002d38922bbe4635896b5872a2fa4ae0_84df088a-debe-4311-8280-9bcc1efd0b73.jpg', 5, 0, NULL, NULL),
(159, 45, '/static/uploads/products/ddc9eba1ef8649d38c3ff429e2991c5a_0efdf210-60df-4130-b74d-0ecdf9016251.jpg', 6, 0, NULL, NULL),
(160, 45, '/static/uploads/products/f4b006ca932a4b7f96c1c6a8e2de7506_110fd147-03b4-4066-abe4-718a6e9b10da.jpg', 7, 0, NULL, NULL),
(161, 46, '/static/uploads/products/be1221855e5447a6ac340bd42d361d8b_937a83b1-45e8-4a82-9d08-48d8f8c1b412.jpg', 0, 1, NULL, NULL),
(162, 46, '/static/uploads/products/9f6ec445abe14aadbf335fba31e5b709_5119167c-9159-4a40-9400-3256b5f1f659.jpg', 1, 0, NULL, NULL),
(163, 46, '/static/uploads/products/dfa960fc09c64454b38e0f2d3dbbe9cc_e580f67c-3d48-4aa2-aebc-f371bc22e666.jpg', 2, 0, NULL, NULL),
(164, 46, '/static/uploads/products/e9f874d43b2142ffbde514299609f72d_bc6b68fc-9b73-4a1e-b656-5ed797915560.jpg', 3, 0, NULL, NULL),
(165, 46, '/static/uploads/products/9d2add5360de4a1f98d7fada9cab0b42_a136db38-6125-4deb-abc9-a698b8b21697.jpg', 4, 0, NULL, NULL),
(166, 46, '/static/uploads/products/ffea863612c54921b1d554f363a4e85a_68afebe4-4932-44fe-9a25-b11d72af1de9.jpg', 5, 0, NULL, NULL),
(167, 46, '/static/uploads/products/a246bf6a5c83409fa6d5887335d96104_b13c5760-d04f-4927-918a-6612bd8e9d4f.jpg', 6, 0, NULL, NULL),
(168, 47, '/static/uploads/products/0c74c9559e6c4b9e992191087cb80763_518f3f6b-bd0c-4b88-8f7e-880742347d35.jpg', 0, 1, NULL, NULL),
(169, 47, '/static/uploads/products/f9853e2f66b34ed0816bae10552898e3_e07a4bdb-0a9a-4bb5-9205-3a7dddcb052e.jpg', 1, 0, NULL, NULL),
(170, 47, '/static/uploads/products/b681b7924c5d4457a8d0db4e36bcd55d_f224a243-1c39-48fc-9857-985ecef8140d.jpg', 2, 0, NULL, NULL),
(171, 47, '/static/uploads/products/8f25f975551f4d638337303ca4d0f742_14faef76-9f81-4c55-98d8-c54e6f67b570.jpg', 3, 0, NULL, NULL),
(172, 47, '/static/uploads/products/a89eae527cac4601bc2012b7e20299ac_ce8a3c28-d2ea-429c-a683-13e0a48f6635.jpg', 4, 0, NULL, NULL),
(173, 47, '/static/uploads/products/b1639ecb734845a3b25a5b54a80b8e6c_59c3b72a-4ba1-497e-9c03-3e5a6f3654d7.jpg', 5, 0, NULL, NULL),
(174, 47, '/static/uploads/products/acb0a7c61b1543f1a69384d8ec3f9ace_76a79a7b-c325-4c3c-9e8c-d68765eefe98.jpg', 6, 0, NULL, NULL),
(175, 47, '/static/uploads/products/81c8654bf69645abafd1704989661595_be016220-2882-4f05-9345-8585086b5e6e.jpg', 7, 0, NULL, NULL),
(176, 48, '/static/uploads/products/b4faba4cd52746529319a920a8eccaee_56ea41c1-fdbe-4a43-9f38-3aaf24671857.jpg', 0, 1, NULL, NULL),
(177, 48, '/static/uploads/products/92d591de4af24969a196f5cd247db717_9911ec28-e3c9-4bb7-bd5f-8e336499c465.jpg', 1, 0, NULL, NULL),
(178, 48, '/static/uploads/products/f004d952f5424cdcb8a96b5c223fa320_16a54e1d-bcdb-4f1a-994d-6dfec348c019.jpg', 2, 0, NULL, NULL),
(179, 48, '/static/uploads/products/003da89bee18459bb22d814cfbea4908_4ca3c966-45fa-430a-9b6e-94bc34b657d7.jpg', 3, 0, NULL, NULL),
(180, 48, '/static/uploads/products/c19921d03cc2472386d2749ba928b7a7_23459da0-f65e-4743-a6bc-3220f4a73702.jpg', 4, 0, NULL, NULL),
(181, 48, '/static/uploads/products/a554d7c1270e41eaae20d7b5196d84bc_2678926d-f3ff-4938-b557-d9b4c5edd61f.jpg', 5, 0, NULL, NULL),
(182, 48, '/static/uploads/products/24ec441ee06745bbadd554d1503eb0ab_d213d18b-40b3-411f-a710-32722ff8962e.jpg', 6, 0, NULL, NULL),
(183, 48, '/static/uploads/products/65f5a31e26a147948bd87bbcd0b6d3a1_8937a0f6-bee1-4fdd-b835-0dd4b89c3ecd.jpg', 7, 0, NULL, NULL),
(184, 48, '/static/uploads/products/d9dc76f1b87a4b7581868a1b92ac4ee6_adc009a8-9f52-435e-87d8-ca411cb7e0b4.jpg', 8, 0, NULL, NULL),
(185, 48, '/static/uploads/products/cac9afdccd6946b28900ee56e07015f4_a05d8238-f216-4c28-a275-cb1f9a8263db.jpg', 9, 0, NULL, NULL),
(186, 49, '/static/uploads/products/59d8afd6fd2a4922a7f867e43159e919_336a2c0e-9537-4c61-af47-aa203156a993.jpg', 0, 1, NULL, NULL),
(187, 49, '/static/uploads/products/f51f1c6fdb044e229bd1e4c276220764_235e5e13-3be2-400f-b622-7021a144d427.jpg', 1, 0, NULL, NULL),
(188, 49, '/static/uploads/products/a48b841679b841f5954c2ba71fa572c3_7bd3804f-3559-4f66-a9df-2ad9f6ea3100.jpg', 2, 0, NULL, NULL),
(189, 49, '/static/uploads/products/9795a509e4cd4d71b9fa4e34b8c7ade9_49f99061-a3ac-4b8d-86da-927d3e87d630.jpg', 3, 0, NULL, NULL),
(190, 49, '/static/uploads/products/3d72a805044940dc9dba43e59d6c9084_a92c88fa-d2a7-4be1-8c5c-ba1d5f60cead.jpg', 4, 0, NULL, NULL),
(191, 49, '/static/uploads/products/7e73efcb9299497f95f4ed1f7c7fd2a8_5fff6bb4-c4a2-4e20-9b79-b9ae6b50144e.jpg', 5, 0, NULL, NULL),
(192, 49, '/static/uploads/products/402bcc78c0894bc5b2599cd986c87f8f_4a97a119-66bc-4ec6-8ba3-7ef9486b5730.jpg', 6, 0, NULL, NULL),
(193, 50, '/static/uploads/products/236e7981b88945fd9afd6cad9b449957_19c4378a-d32f-48d8-9ed5-446729b0156d.jpg', 0, 1, NULL, NULL),
(194, 50, '/static/uploads/products/25589759e6f54087b4c1dc8b4afac113_43d91fc6-a091-4b73-98c2-82ad703e6beb.jpg', 1, 0, NULL, NULL),
(195, 50, '/static/uploads/products/4fca2629acf846aca4d01b76da2804f8_cdea7570-7c6d-40f8-afaf-77b5f67d7233.jpg', 2, 0, NULL, NULL),
(196, 50, '/static/uploads/products/6ba31f3c23a349dd92b462a495f5733f_e40d5591-49f6-444d-862c-10c14c2f29ac.jpg', 3, 0, NULL, NULL),
(197, 51, '/static/uploads/products/acd388901c784a49a58a10b53e94e917_4092b0a6-028f-4d4f-a5a7-3d599b07c6cb.jpg', 0, 1, NULL, NULL),
(198, 51, '/static/uploads/products/6a9948e8deeb4532921bf62d62a242a6_7748ff0f-23eb-4e32-b058-92026c446d60.jpg', 1, 0, NULL, NULL),
(199, 51, '/static/uploads/products/f692ea75af8c416095200876c4d18e4b_e50867a9-7fb8-4b75-8180-1b81dfbd9dab.jpg', 2, 0, NULL, NULL),
(200, 51, '/static/uploads/products/42a864fb7d564966a35b71d43c19d087_f55a8cbe-d324-4ec1-ba4b-b47c321eefe2.jpg', 3, 0, NULL, NULL),
(201, 51, '/static/uploads/products/0a2ee50f45cc472ea24250315912bc53_46717fb3-d0a6-429c-9e02-f425ad97a596.jpg', 4, 0, NULL, NULL),
(202, 52, '/static/uploads/products/47ae8220959f4de4b5d9cd7c4e99d070_c4bfa36e-d46a-41a3-a04c-af7089d68614.jpg', 0, 1, NULL, NULL),
(203, 52, '/static/uploads/products/10d660ff12d844838604b403248de5e9_642eb8db-91fb-474e-a201-7fd0c01fb92d.jpg', 1, 0, NULL, NULL),
(204, 52, '/static/uploads/products/4fde6e8bebc74d259e7c865178747a0e_10a784ae-70fd-449b-9eb4-363d525b386f.jpg', 2, 0, NULL, NULL),
(205, 52, '/static/uploads/products/80ff6004f0994c88b353f42206e62474_312aa327-86d6-4e74-8568-bf0ce53728ff.jpg', 3, 0, NULL, NULL),
(206, 52, '/static/uploads/products/b3ac6d4f7fdf45bea3de65417d94c715_1f45d55d-434d-4ad0-ad24-9d2c07e269dc.jpg', 4, 0, NULL, NULL),
(207, 53, '/static/uploads/products/faaeabfc71634e7d9f23ec348d4c3d84_d96e2dfa-8d8c-4335-a9f9-8bbd8daa6e89.jpg', 0, 1, NULL, NULL),
(208, 53, '/static/uploads/products/123679201dd34cd989900d8f6ae37c29_bce89d16-e926-4a3e-87db-cce76bc788a0.jpg', 1, 0, NULL, NULL),
(209, 53, '/static/uploads/products/4de00411b1864571b4d722e3a378275b_293af7df-6a4a-4218-8d39-746fb957943d.jpg', 2, 0, NULL, NULL),
(210, 53, '/static/uploads/products/782fa01f1dce4392b643a9a32e68ce7b_f5bca650-dfae-46d7-9427-1db2cd3b4224.jpg', 3, 0, NULL, NULL),
(211, 53, '/static/uploads/products/b0dda903d409444bbeb2b503eb7e1b42_95a2b5a7-1a13-47f9-93e1-6bbca7f92e1e.jpg', 4, 0, NULL, NULL),
(212, 53, '/static/uploads/products/d2a2111e367141adb980c66e8bfe0834_b503cc55-70fc-4812-a012-7f7c84d7e6e2.jpg', 5, 0, NULL, NULL),
(213, 54, '/static/uploads/products/8d0934c2977441418f776f5a0b1b1d5a_d363209a-0316-4e6f-a5d6-5e8fbbb7cb72.jpg', 0, 1, NULL, NULL),
(214, 54, '/static/uploads/products/aeaf284938a24703aa784b6925e5d4ab_d4d2e0ee-ec04-4d1c-b68f-bef5f0116915.jpg', 1, 0, NULL, NULL),
(215, 54, '/static/uploads/products/aff0c1704c2b406db2ac5c4caf6baeab_13c70302-957c-43ff-ac9c-1eb72b348e0e.jpg', 2, 0, NULL, NULL),
(216, 54, '/static/uploads/products/28ca69f7fe08435eb4b8988f88600289_5b191d1a-436b-4000-88e2-97b097731b8d.jpg', 3, 0, NULL, NULL),
(217, 54, '/static/uploads/products/97c3b9800b1c47cc8a1c76db773f20e2_b3cdebe2-c3f3-4382-a1ec-1cb97b5101d4.jpg', 4, 0, NULL, NULL),
(218, 54, '/static/uploads/products/c81b0534afd04befb3c2eebc15209b2f_94fcc0da-1f43-489f-8156-243e34a7abcf.jpg', 5, 0, NULL, NULL),
(219, 54, '/static/uploads/products/24681f48f1f046ecb86670139f1c3a7a_b4eddcbd-7f3d-4afa-be31-b5b5cd73956f.jpg', 6, 0, NULL, NULL),
(220, 54, '/static/uploads/products/6d2fe94de7b2435a9b97526492b6f892_aebd1ca3-c764-48db-9cb9-ee33a2684de8.jpg', 7, 0, NULL, NULL),
(221, 54, '/static/uploads/products/94dd5e13a91841d7b1c5400727b5bf61_654111d2-eeae-418e-87d8-27d81aeab267.jpg', 8, 0, NULL, NULL),
(222, 55, '/static/uploads/products/d7c484f41a024d6d9a6c90a4b775e0be_e630b363-713e-4608-ad32-0c7be066fe30.jpg', 0, 1, NULL, NULL),
(223, 55, '/static/uploads/products/156c18a29dee43179e3ed26fea19efc0_bb44f090-6b8e-41bc-bf8f-3b8cdb9de2b5.jpg', 1, 0, NULL, NULL),
(224, 55, '/static/uploads/products/99f07e0e04cf4d049f390a2b77b677ee_f0c8948b-385f-4630-b6b0-41147bbabd66.jpg', 2, 0, NULL, NULL),
(225, 55, '/static/uploads/products/2aea52c4345842438939a6eb21a27acf_291ee16d-dffb-4edb-8734-303933c34ef2.jpg', 3, 0, NULL, NULL),
(226, 55, '/static/uploads/products/3c579554cb114083b8d9f67a74ba10d3_94dc7fd6-e332-4405-a570-037269d6ccf4.jpg', 4, 0, NULL, NULL),
(227, 55, '/static/uploads/products/4e5cd76cd44f45a8bced0b6bba51c58c_bf90da1a-3f3f-435e-a3e9-face10788166.jpg', 5, 0, NULL, NULL),
(228, 55, '/static/uploads/products/4e2080ef4b0b412c8ca4580dc8075e09_648282a4-1858-4661-bc98-ea1dde4ceb97.jpg', 6, 0, NULL, NULL),
(229, 55, '/static/uploads/products/7dd7469ade494b7396545f29c7f68f8a_a7b61add-4959-433a-9863-90cfa3db565e.jpg', 7, 0, NULL, NULL),
(230, 55, '/static/uploads/products/556780e2798a450b9bc5beb555c55e7b_2bb28018-570f-4629-a7e2-e08527f0a561.jpg', 8, 0, NULL, NULL),
(231, 56, '/static/uploads/products/43b0ca08582249a28bf45af271976e94_55789241-6028-4982-a24f-8d92713a9189.jpg', 0, 1, NULL, NULL),
(232, 56, '/static/uploads/products/e713c0fd79d144cf9b50aceaf7894f1a_8ea3f6fc-8e22-42b9-bf0c-1fb4e0d6f379.jpg', 1, 0, NULL, NULL),
(233, 56, '/static/uploads/products/2e27d81b902d404ca1e644fb93da9ae7_fe1b8906-0717-44ca-8865-b78402466fcc.jpg', 2, 0, NULL, NULL),
(234, 56, '/static/uploads/products/2d8fa93d8abf4230aeb68f8ae7ad5e35_ef74dd18-ca04-4e29-8849-2e490b888371.jpg', 3, 0, NULL, NULL),
(235, 56, '/static/uploads/products/c9f17baa42c84ddc980da25e8ff76094_f2fe29ea-a024-4a4e-a62a-d601ee78a237.jpg', 4, 0, NULL, NULL),
(236, 56, '/static/uploads/products/c558ef0657e2460baf517ce80b28e071_c85c42ea-07a9-4066-bd80-2d606036ef48.jpg', 5, 0, NULL, NULL),
(237, 56, '/static/uploads/products/88879c1b5b7a47f6a92ad02e923e5148_7b3f12ba-a61d-4d34-827e-422ec42cd6f1.jpg', 6, 0, NULL, NULL),
(238, 56, '/static/uploads/products/afd5bba1c98747d4a0a6d36838ed2875_21d938da-c666-4d63-952a-33b80545bc9c.jpg', 7, 0, NULL, NULL),
(239, 56, '/static/uploads/products/d4995009b9fc48c980bcf21d38bade18_37a3fc13-2f04-4cfc-8c6f-82360eae7bf8.jpg', 8, 0, NULL, NULL),
(240, 56, '/static/uploads/products/4a68bad8918e432e9c20bf5876e85794_a119d2dc-a056-460a-b3f9-a3e95da31d4d.jpg', 9, 0, NULL, NULL),
(241, 56, '/static/uploads/products/2ac516bb1cfa4f6982cc63bb8eb3e599_d93d0872-ff2b-4d4e-b703-a0a98e2dc810.jpg', 10, 0, NULL, NULL),
(242, 57, '/static/uploads/products/a421e3bebd6c4c828deff3d3a3fcfd76_c7d89c1b-0dbf-4443-81b6-ec986cdca1b5.jpg', 0, 1, NULL, NULL),
(243, 57, '/static/uploads/products/00d7de433dd744939260860c82958d5a_5a6aaac4-b91d-4998-8e21-30fcb3f14104.jpg', 1, 0, NULL, NULL),
(244, 57, '/static/uploads/products/b7e7582fbad8493d8b297f772776066a_8d4e2444-15fc-45ef-b95e-f6dab4ff7c0d.jpg', 2, 0, NULL, NULL),
(245, 57, '/static/uploads/products/d0bcd190de484d96af9bdd081775c530_8ef499c7-3f21-4142-9756-48a62493f80e.jpg', 3, 0, NULL, NULL),
(246, 57, '/static/uploads/products/3ae01c434667469ba064244dda8949c7_799d1970-bcb1-4145-b00c-7e398d69242c.jpg', 4, 0, NULL, NULL),
(247, 57, '/static/uploads/products/6dbc4772d44d488dad2d3e6cec98c5bb_dee1641f-3cc3-4987-963b-05db976dcf20.jpg', 5, 0, NULL, NULL),
(248, 57, '/static/uploads/products/5829d5838e81463d914814624f1227c7_bae17b79-14cb-426d-8604-99819977b976.jpg', 6, 0, NULL, NULL),
(249, 57, '/static/uploads/products/63e5da4d4c4142258093e49fcd260ad6_c9709763-cb3e-4213-aa44-d5d00ddd7e80.jpg', 7, 0, NULL, NULL),
(250, 57, '/static/uploads/products/07d527b3b7f6495091b6ea80a9e3de06_b7a86b13-28fb-4a4c-9b77-a664dd29171f.jpg', 8, 0, NULL, NULL),
(251, 57, '/static/uploads/products/dcd41a9494da4d1d8656ea606ce6af8f_fad11648-c152-4651-acab-1d80c6033c5e.jpg', 9, 0, NULL, NULL),
(252, 57, '/static/uploads/products/c374255c13dd4836ab2529338f1e8226_db1ef2ad-2b11-4c34-8b09-ec76e8b4e12e.jpg', 10, 0, NULL, NULL),
(253, 57, '/static/uploads/products/97c5c071a5f645f7a384b08663257a62_b6097dc0-9f83-41fc-9701-9bbf74f8a64b.jpg', 11, 0, NULL, NULL),
(254, 57, '/static/uploads/products/d2f9cb15755e4fd8a681fdd00284e05d_6d060cac-3a4e-4f5f-af71-084bb2b168a9.jpg', 12, 0, NULL, NULL),
(255, 58, '/static/uploads/products/7c7be06f2b6d4f8aa1ff9361e90c9b70_517befbc-8198-4fed-8340-3b72dfebb789.jpg', 0, 1, NULL, NULL),
(256, 58, '/static/uploads/products/b0fb02d4f52b4c4796e86640a7b26fd8_87618aa9-1b51-4e8f-aba8-b4b5f1a9a3a6.jpg', 1, 0, NULL, NULL),
(257, 58, '/static/uploads/products/f642e41e33644cfe8ddaeee4ac76f07d_6dde7553-934d-4a4d-8c78-c15628c5265c.jpg', 2, 0, NULL, NULL),
(258, 58, '/static/uploads/products/a978795fa408403c9bb4c77a9f0847de_52f6186e-2d69-4f2a-9327-ceee61e9a5f2.jpg', 3, 0, NULL, NULL),
(259, 58, '/static/uploads/products/d9e4c6552a2d418d939940885f5e1141_614ad8a7-9f43-4421-b827-07ba4d455455.jpg', 4, 0, NULL, NULL),
(260, 58, '/static/uploads/products/2d8a042bca434743a3cebd9c4b2df1c2_17829b67-9046-4e37-b52d-a94c2d0b2485.jpg', 5, 0, NULL, NULL),
(261, 58, '/static/uploads/products/1658383c26bf4ab5a675d070f22ac108_d3d5fcfb-7c32-4e3c-8d7d-cca0d2650e4c.jpg', 6, 0, NULL, NULL),
(262, 59, '/static/uploads/products/3d47a742db1d4cd4ad8bfd316ffbf56a_3960afb7-8dc2-487f-ae17-6b63c7f7a4bb.jpg', 0, 1, NULL, NULL),
(263, 59, '/static/uploads/products/5de46671a8fc4d17abe9580671824f8b_b39acf00-259c-4df4-9773-cd1813bddef9.jpg', 1, 0, NULL, NULL),
(264, 59, '/static/uploads/products/43dc741e92dd4a89b69142a39fbb6b00_759f8c5d-f92b-4fb4-bf32-2ff49b0b4d0b.jpg', 2, 0, NULL, NULL),
(265, 59, '/static/uploads/products/49b364e8f3eb460d9c1b4be9a3660d3e_dd26a373-9f83-483e-92c7-a85a5d89e76c.jpg', 3, 0, NULL, NULL),
(266, 60, '/static/uploads/products/121d718d7f2c4553b0ab9582714018cf_e9662b09-1407-40c6-9dab-0fb9d9b9a7c0.jpg', 0, 1, NULL, NULL),
(267, 60, '/static/uploads/products/069be1a1762442f18690d436c74bc7ab_30db6b82-0347-4c32-b697-90b668837486.jpg', 1, 0, NULL, NULL),
(268, 60, '/static/uploads/products/e5a507f056b140d6aab21cd905b5b0e7_cc54bbcf-392a-47d3-9c85-32516bfd0e4c.jpg', 2, 0, NULL, NULL),
(269, 60, '/static/uploads/products/70da669bc2e74b41ac421c2c95368bb2_f8900ce5-cc70-4145-b86a-b92c33b111af.jpg', 3, 0, NULL, NULL),
(270, 60, '/static/uploads/products/d71ab2639fa14d34b219c18bd8cc055d_d67bf02b-2bf7-4491-88b9-a0374ea45e8e.jpg', 4, 0, NULL, NULL),
(271, 60, '/static/uploads/products/d87295060875497f89cff45e818d4376_f1c15b92-3d14-4225-8c61-134360330e68.jpg', 5, 0, NULL, NULL),
(272, 60, '/static/uploads/products/a2a0d502adec485783475a66f9dc9c30_1d055b05-1d5e-4cad-8752-547005dc0f75.jpg', 6, 0, NULL, NULL),
(273, 60, '/static/uploads/products/5fe963ed50194019963ca52766f73081_27ae1833-05a5-4f8c-be2c-cae405040f91.jpg', 7, 0, NULL, NULL),
(274, 60, '/static/uploads/products/e84f5dc912d94ce1b0fcf5cc07599fd3_b3712e37-bd1f-4581-bff6-c6629589b250.jpg', 8, 0, NULL, NULL),
(275, 60, '/static/uploads/products/4ebeb72a6be24b118f14735b31746d85_ba11cc34-b976-4a4c-acfd-6ea26ca11d3e.jpg', 9, 0, NULL, NULL),
(276, 60, '/static/uploads/products/92785952afd242dcb7bead147e314c20_312ccafe-f818-4272-886c-6d4f334b129f.jpg', 10, 0, NULL, NULL),
(277, 61, '/static/uploads/products/d467f2253e864071a27a83f0b1bead6a_215b18da-e8c3-4766-a36d-566b70a71987.jpg', 0, 1, NULL, NULL),
(278, 61, '/static/uploads/products/a5a8221e9d564c8fb48be3d034c44069_c3255922-0d2c-4d24-a2b7-728986bed0a3.jpg', 1, 0, NULL, NULL),
(279, 61, '/static/uploads/products/6b57e3a0b40c453f9c16fea7e78373b2_24e3c97b-1e51-43c9-a8c4-090ce9b7d118.jpg', 2, 0, NULL, NULL),
(280, 61, '/static/uploads/products/de6890acde154fbcb7e733769b90ef94_933c4379-ae3b-479b-8d00-764c12fb4bee.jpg', 3, 0, NULL, NULL),
(281, 61, '/static/uploads/products/b27a1e36d4fa416eb668d3b4cf7715b3_02fd023e-12c3-43b4-b733-6d68010d802d.jpg', 4, 0, NULL, NULL),
(282, 61, '/static/uploads/products/e626cb5d4f9a4ad88c94fdb55cbcd152_fe5ddee2-8bfd-489c-be4d-f26243e1f29a.jpg', 5, 0, NULL, NULL),
(283, 62, '/static/uploads/products/b1dc6d1dab3b4cc8898a260e0e105203_f6751718-00cb-42a2-b4b5-58bbf1b0e836.jpg', 0, 1, NULL, NULL),
(284, 62, '/static/uploads/products/6df4acffc1ad4719aeac4a61e7e02826_b8594018-cf84-4155-aeb1-567d2ac7b14d.jpg', 1, 0, NULL, NULL),
(285, 62, '/static/uploads/products/a3845c5bf80c4657a97c98107ed08267_160856dc-62b5-4bce-afdc-39cc71b19a07.jpg', 2, 0, NULL, NULL),
(286, 62, '/static/uploads/products/5da0e0cad00b454f92e042854760824d_06eff839-0582-4992-bc77-ae989df9055c.jpg', 3, 0, NULL, NULL),
(287, 62, '/static/uploads/products/9df8246c152b4e9f9e0edc0df1fa41ed_35d19513-faef-4b00-8d86-a0660d55631d.jpg', 4, 0, NULL, NULL),
(288, 62, '/static/uploads/products/14e1ac43105f44398ec87674a77658ac_e751dd6c-629e-4543-bd84-457cfa82aec8.jpg', 5, 0, NULL, NULL),
(289, 62, '/static/uploads/products/b908f07fd0db47f0b5d634c5c0ca3cb1_0697fbdb-2b77-419c-b357-59aa0c44b81f.jpg', 6, 0, NULL, NULL),
(290, 62, '/static/uploads/products/4390557a71db433ba8b5aef2c96dabe1_e2ff98df-23a5-4776-bc51-52cd29101a0d.jpg', 7, 0, NULL, NULL),
(291, 63, '/static/uploads/products/21f1c02aa7fb4ba5a757dddeca02e9b1_1423067e-d3e8-4652-9c5b-0edef37f9281.jpg', 0, 1, NULL, NULL),
(292, 63, '/static/uploads/products/9c786982320a4c3cbb3f9cc2f77fd426_7f916f29-4257-4e7b-b256-b7cff236f212.jpg', 1, 0, NULL, NULL),
(293, 63, '/static/uploads/products/c9167df71fd045f4a61423836e368f44_9500034d-c515-4821-b6ba-a89085e9cd6d.jpg', 2, 0, NULL, NULL),
(294, 63, '/static/uploads/products/89bf82b6450b4c71a04526f4764f8f51_37d74401-a8e2-49de-9c93-b886977c6f0a.jpg', 3, 0, NULL, NULL),
(295, 63, '/static/uploads/products/6ff1109276d84b67b94c5d6424382ea9_c9953fd0-80e5-4724-8701-e5b27d622179.jpg', 4, 0, NULL, NULL),
(296, 64, '/static/uploads/products/e2ebf5ddb1e54dd7958ffbfb79e5b002_fcc1d112-074b-4db4-8f63-ed737cc8de90.jpg', 0, 1, NULL, NULL),
(297, 64, '/static/uploads/products/90ff574f89ad4708aee626ecb78faba8_ca1054a9-aca6-47c4-8106-f3405bb0ab0a.jpg', 1, 0, NULL, NULL),
(298, 64, '/static/uploads/products/b1bd793393584d3ea3f9234f39e772be_df3678ad-8d58-4f26-a75a-4f5920995156.jpg', 2, 0, NULL, NULL),
(299, 64, '/static/uploads/products/9678b74ea7d6493ca5b9a054b61ee5b9_bfa77113-4e55-42d3-a248-b654ecfc7cfb.jpg', 3, 0, NULL, NULL),
(300, 64, '/static/uploads/products/1aae89bbc8cd4d64be2e92b7d6aa4660_c3914406-c19c-40c9-8a2c-14470b996a6f.jpg', 4, 0, NULL, NULL),
(301, 64, '/static/uploads/products/f56a7c1e06fc4fb9a081d375a289ad9d_d56bc610-6aba-4960-802d-71118ec34179.jpg', 5, 0, NULL, NULL),
(302, 64, '/static/uploads/products/561e8b6d460445d88747c5bdba022e0d_f9aad310-32f8-49cc-a4bb-ed8fae110290.jpg', 6, 0, NULL, NULL),
(303, 65, '/static/uploads/products/f020a002dcf44fbc88b81804ec5934e2_ba8660c4-df34-4627-aca1-ecfdbd105986.jpg', 0, 1, NULL, NULL),
(304, 65, '/static/uploads/products/d81c863a350f46d98787d31cfe8a3425_ec1ff322-0d34-42a5-a7c1-a6aae6599e58.jpg', 1, 0, NULL, NULL),
(305, 65, '/static/uploads/products/439c0487864c4fe2bcccdc2c3ea83519_9b358465-946c-498b-b29c-da5725743e67.jpg', 2, 0, NULL, NULL),
(306, 65, '/static/uploads/products/2331a6e36a254ab4a494781b8f87d9d1_b06fe2f9-00c4-475e-841a-815955aa74f2.jpg', 3, 0, NULL, NULL),
(307, 65, '/static/uploads/products/4cb6305c51d24c73b519a903a70e1a00_38268097-e14c-46dd-a827-2f1b509be622.jpg', 4, 0, NULL, NULL),
(308, 65, '/static/uploads/products/3174b542a6a947efa654800340bb69ab_5c33a15e-914d-4097-ac5c-ae65f245910e.jpg', 5, 0, NULL, NULL),
(309, 65, '/static/uploads/products/1250704d37a34e52980dddcad0ea15e2_6e9cd8ae-406a-4d95-a7e9-3fe22f8698ed.jpg', 6, 0, NULL, NULL),
(310, 65, '/static/uploads/products/354cb33a2f624319a07571c4d9ce4a4b_bb7728dc-a1c6-43ec-8e90-3708aceed7f0.jpg', 7, 0, NULL, NULL),
(311, 65, '/static/uploads/products/ddbfa2d045ea4fe6b9db45cac37acd55_8f78b327-f264-41a3-bfb6-c8a081d07538.jpg', 8, 0, NULL, NULL),
(312, 66, '/static/uploads/products/4cf97184281541b599e525bd6203c130_710011f6-fbf6-42de-91af-14f09123d9f9.jpg', 0, 1, NULL, NULL),
(313, 66, '/static/uploads/products/26c166e5ce2c4f4ba3a1bfe582c33bf7_013a30da-4689-4388-83ad-471b2ac0457d.jpg', 1, 0, NULL, NULL),
(314, 66, '/static/uploads/products/aff5f75b92af4e1d9172e67587d86787_c185bea3-6a4e-4cb0-b877-b11052f7d3b4.jpg', 2, 0, NULL, NULL),
(315, 66, '/static/uploads/products/2eb6b235c04d4bdc9774885afa99d2fa_24a755a9-af92-4ce5-8df1-7d1de18d301e.jpg', 3, 0, NULL, NULL),
(316, 66, '/static/uploads/products/c0ae8357988c4b638fd258c063ad5e24_a9c845f3-e8bf-46d6-aaf5-b33b02a55f7c.jpg', 4, 0, NULL, NULL),
(317, 66, '/static/uploads/products/aa0aedb089b34396b35b8665500852e7_54edfff0-b3da-4e86-bd9b-711a09b814c7.jpg', 5, 0, NULL, NULL),
(318, 66, '/static/uploads/products/b505c4d1dff545b3bbc5d0fc54dd6f4d_2214330b-d92d-4b78-8ba6-fdae7f32f24c.jpg', 6, 0, NULL, NULL),
(319, 66, '/static/uploads/products/5cfecb3ee9b94f0297fed1474c53c243_34ad1008-4f0d-4c66-a319-db60b78f787d.jpg', 7, 0, NULL, NULL),
(320, 66, '/static/uploads/products/72ad28c0744f46019d3366cee6982d13_b86367ba-43fa-4ce5-9d54-eca26c207b5e.jpg', 8, 0, NULL, NULL),
(321, 66, '/static/uploads/products/a1e1b7e65f284c4e8bdf243dd0291f15_6f537518-d6cc-41cc-9cd4-a9903670919e.jpg', 9, 0, NULL, NULL),
(322, 66, '/static/uploads/products/d3286e60513f4b61895d3dd6a8fee5a3_05d418af-b3f4-493a-bd5a-41dddd9590d7.jpg', 10, 0, NULL, NULL),
(323, 66, '/static/uploads/products/0f5edcb5adc94fdfa29c139f1f3a8eeb_315fb1c6-8186-4a3e-894c-8f6308ccd694.jpg', 11, 0, NULL, NULL),
(324, 67, '/static/uploads/products/f4f2322660e34e4996a34e4b3fe242c5_aa3685a4-c9b0-4ba3-aaf1-b2ae1806f407.jpg', 0, 1, NULL, NULL),
(325, 67, '/static/uploads/products/45bfa02d7d72416bb5fbd9ff607e8c0c_c1435b96-4e3e-467f-ae4d-5df1602312e4.jpg', 1, 0, NULL, NULL),
(326, 67, '/static/uploads/products/0e2430ec56974d75a8bb436d2dae9c43_ad325b2f-ea41-4f30-88d2-c6cb4a59c8f2.jpg', 2, 0, NULL, NULL),
(327, 67, '/static/uploads/products/aed0ce1fd0d3459486229a24aeb33355_16d48dc7-1aee-4172-9e69-f9a67648eecc.jpg', 3, 0, NULL, NULL),
(328, 67, '/static/uploads/products/4c423a1b08844334b3a708a4b7915dc0_345fa7df-34b5-42af-b27e-897682b542ce.jpg', 4, 0, NULL, NULL),
(329, 67, '/static/uploads/products/857b4601a4914ca4bc864de35642c904_850c1ebf-1603-4e4d-becb-730f31b5da32.jpg', 5, 0, NULL, NULL),
(330, 67, '/static/uploads/products/bd722942f5ca43eeb639f19aa2474040_313fe324-c71d-4eca-855d-a1687e2c3f9c.jpg', 6, 0, NULL, NULL),
(331, 67, '/static/uploads/products/15acaf79907d45c091e501f8552c9be3_c59aede5-e513-474f-98fb-5723b16942ce.jpg', 7, 0, NULL, NULL),
(332, 67, '/static/uploads/products/48505853e5d141acaac1b39487735d57_e0014e45-f2f7-4f5e-9b0c-934b37035cef.jpg', 8, 0, NULL, NULL),
(333, 67, '/static/uploads/products/b528b7877e034e1899308d9aba96ff77_0398df6e-6282-42ff-8724-450ec1837a3e.jpg', 9, 0, NULL, NULL),
(334, 67, '/static/uploads/products/199bf590d36a4fa8855b75d63a502c94_6d751f60-50c8-4d30-9367-593d703ca46a.jpg', 10, 0, NULL, NULL),
(335, 68, '/static/uploads/products/770ebab0dc38488f84aa11bea4fd4694_bdb7acad-5eaa-4779-bb5b-c0f26c45e11c.jpg', 0, 1, NULL, NULL),
(336, 68, '/static/uploads/products/00552c2a27234ad28de6af0be4cbfb03_6191a70e-aa6b-4c0f-904e-894481d41469.jpg', 1, 0, NULL, NULL),
(337, 68, '/static/uploads/products/ab26e71ed4cf454baa2d5335ebbafc34_9f8de20f-444f-4f1e-8f14-994fb3269206.jpg', 2, 0, NULL, NULL),
(338, 68, '/static/uploads/products/882e28cb9d6347388e1becb4b5e8c2ff_71ca90ba-bf34-41fc-90af-9aa38a0fff35.jpg', 3, 0, NULL, NULL),
(339, 68, '/static/uploads/products/aaeaf354945f4f2592d18f8a89afa8ed_74290c4b-d682-4492-9c06-b5ef53670629.jpg', 4, 0, NULL, NULL),
(340, 68, '/static/uploads/products/91c4d1016d794b8a8728235ebadcbcb1_1a37d2eb-ed30-47c7-8ae1-7e82576c9f76.jpg', 5, 0, NULL, NULL),
(341, 68, '/static/uploads/products/54ab0e67a78f4b64a2eeaed6d12d3841_6e29baab-dfd9-4c08-9c75-e235edb6a245.jpg', 6, 0, NULL, NULL),
(342, 69, '/static/uploads/products/5dd9119b395247fe8db00aaae3a3516a_de4b96f5-fd09-4ccc-b05e-0cf90c9d9577.jpg', 0, 1, NULL, NULL),
(343, 69, '/static/uploads/products/8fbd79f05e6d405f88c0540dd29a13f4_1194a692-95a4-4ad2-a555-6eab4a18fab4.jpg', 1, 0, NULL, NULL),
(344, 69, '/static/uploads/products/9439b63bf2bb427da7531fab352d3e9d_70d7eb81-a6b3-4a6d-9e1d-639348109da4.jpg', 2, 0, NULL, NULL),
(345, 69, '/static/uploads/products/b77324d551ee4c37bfdf98ffea647f0c_805ba17b-8764-4bb0-b155-abf0759ac265.jpg', 3, 0, NULL, NULL),
(346, 69, '/static/uploads/products/104b3a139f2b41b2ab502e4b51f7bf44_d74759a4-ef0b-4eb1-9c3c-54113602abc2.jpg', 4, 0, NULL, NULL),
(347, 69, '/static/uploads/products/6fef3246474840ef8f1c37eae4b2eebf_72a70a0e-3c16-4491-8b4a-3c8be6dd6d62.jpg', 5, 0, NULL, NULL),
(348, 69, '/static/uploads/products/15da1972453d4717ad4c14b5f33b1230_31e61ca2-51bf-4579-9401-0ed454e3c5be.jpg', 6, 0, NULL, NULL),
(349, 69, '/static/uploads/products/dcf0e8e795c344bb9c154331ff2f7c35_25513ea1-a331-4d56-aff1-8eae0a7990cd.jpg', 7, 0, NULL, NULL),
(350, 70, '/static/uploads/products/ce49a6b326404897a9c1a2133a6f1734_ad91a09e-027e-4ad3-9afd-9b466a4ee575.jpg', 0, 1, NULL, NULL),
(351, 70, '/static/uploads/products/84b383fcfb82420abf62ec4a5ba14536_11eb6e77-3f68-46bf-b860-4092a80e36e9.jpg', 1, 0, NULL, NULL),
(352, 70, '/static/uploads/products/4042f886f9f44857b33d0aedeaed8a2e_752451ab-8603-4d17-8b13-f18983406564.jpg', 2, 0, NULL, NULL),
(353, 70, '/static/uploads/products/27cbac5945be4aeaab19fcbdb8fa5b71_99da8297-bc76-46a8-85d7-b33f0c0b6466.jpg', 3, 0, NULL, NULL),
(354, 70, '/static/uploads/products/ede3f9dc8e4a43f5a0298144dc6b21cf_187080d2-7604-47c4-b5ac-4f1adbd6befa.jpg', 4, 0, NULL, NULL),
(355, 71, '/static/uploads/products/ce124076a7584e57a46cdcbba5ef9902_a973da83-9546-475a-b893-aa8f296b7b26.jpg', 0, 1, NULL, NULL),
(356, 71, '/static/uploads/products/3531c6a9e4b547ab8dffab1900c6ce64_dcb47e09-cf69-4e15-9c77-93b3ab9a9a8b.jpg', 1, 0, NULL, NULL),
(357, 71, '/static/uploads/products/d366cc7a93b44254b5c70bfcb419e44b_7b696e46-590e-4066-a861-4a175c6e54a0.jpg', 2, 0, NULL, NULL),
(358, 71, '/static/uploads/products/3317d176e0c24d4e8e53403f2cd337c0_66850a8a-8863-4839-90cc-1bcfe518883b.jpg', 3, 0, NULL, NULL),
(359, 71, '/static/uploads/products/3e3573696d7a49449ec2b2dfdb5cfd62_2ffbe710-1e98-4859-bed2-a71e7cee4843.jpg', 4, 0, NULL, NULL),
(360, 71, '/static/uploads/products/25a7fc0150e946f083473a4613521677_a54355c7-cdbe-48c4-97ee-1ed94fae7add.jpg', 5, 0, NULL, NULL),
(361, 71, '/static/uploads/products/d37aad2d70234dcc90043d19a7987a36_9c4c774b-b491-447f-89e2-103e7c7fd123.jpg', 6, 0, NULL, NULL),
(362, 71, '/static/uploads/products/f2a1abd494b6442999ce0627c01043d8_8daac095-d360-429f-a7b0-5f2e2f91cb0a.jpg', 7, 0, NULL, NULL),
(363, 71, '/static/uploads/products/e5a1b03ba7054e848768407421b40dae_84033e66-0738-4a6d-94c0-cbbf28e6b5f7.jpg', 8, 0, NULL, NULL),
(364, 71, '/static/uploads/products/4c77f92ba20741e7b2cf267d70297b05_89c01ea4-3abe-42ea-ae64-921cd220a6c0.jpg', 9, 0, NULL, NULL),
(365, 72, '/static/uploads/products/e7a021dc3c874737a27adb3e0f407282_7b9cc249-52ff-4c6d-bb68-dd173b13c14e.jpg', 0, 1, NULL, NULL),
(366, 72, '/static/uploads/products/29c9f67562604cbbb04f1538d0170e47_91f7bb71-dc22-4b82-8a3f-ec4584badc21.jpg', 1, 0, NULL, NULL),
(367, 72, '/static/uploads/products/369e8a6328ad4c7bb9f01220d09b5487_56b9ffe3-94fc-4593-860c-c776d6f48550.jpg', 2, 0, NULL, NULL),
(368, 72, '/static/uploads/products/607130f3db7d490a9a99bbc054b6625a_f5a74170-3bac-464a-8dca-2e5d7ffa39aa.jpg', 3, 0, NULL, NULL),
(369, 72, '/static/uploads/products/fd6d29757bc0497989cb2c1785b16861_6f62a037-b3d1-4f94-a657-3cc28b17663a.jpg', 4, 0, NULL, NULL),
(370, 72, '/static/uploads/products/574b00c2d3d0417b80e754ab53053dcb_f7797e84-2122-4001-ac39-ef3995ff808c.jpg', 5, 0, NULL, NULL),
(371, 72, '/static/uploads/products/84b5052cd7a94dfbb13298eb6efe9b2c_8730d92c-eca9-47fa-a87d-3be3828e83b2.jpg', 6, 0, NULL, NULL),
(372, 72, '/static/uploads/products/b2ccdbf1194b4dd1ab3b8072cf947d5f_86417d41-c771-4558-b938-abf252b91bbc.jpg', 7, 0, NULL, NULL),
(373, 72, '/static/uploads/products/6a51035743184d5d8dbd88e9fbc41d5a_3dade3eb-421a-428d-9f39-58c6a05055c8.jpg', 8, 0, NULL, NULL),
(374, 73, '/static/uploads/products/376a28375638426f8228c4917b8a4470_6ac990fc-2724-47b0-baef-95294f6df661.jpg', 0, 1, NULL, NULL),
(375, 73, '/static/uploads/products/8d2d655a046e4d37a7e654a8e2cfdd55_a54ff88b-2349-414c-812f-b7e2897a6f62.jpg', 1, 0, NULL, NULL),
(376, 73, '/static/uploads/products/e1e3f97ee71f4499bb608dbdeb812116_94c145d2-d22d-455a-ac46-ac890270feee.jpg', 2, 0, NULL, NULL),
(377, 73, '/static/uploads/products/703dbe687d354ea6824fa48ef76e777b_3a869d37-387b-43b9-b947-75af8f22f500.jpg', 3, 0, NULL, NULL),
(378, 73, '/static/uploads/products/6497669549474f7c936b675f6d255efe_1f749e92-d35e-471a-aa84-62785e43e0b9.jpg', 4, 0, NULL, NULL),
(379, 73, '/static/uploads/products/010289108f8d4269a48610c9d2e06b6e_634c9f6c-d50c-4f2e-9c42-224c7800b7d6.jpg', 5, 0, NULL, NULL),
(380, 73, '/static/uploads/products/4963d6a6bcde464492dfb8c18b5208fa_2db690b4-b7cf-4b9d-9f5b-9443749c6e64.jpg', 6, 0, NULL, NULL),
(381, 73, '/static/uploads/products/d04e09eea059466a8bc90624999ccfd9_aa30862f-2554-4833-acb1-56c22811757c.jpg', 7, 0, NULL, NULL),
(382, 74, '/static/uploads/products/1648f6526c5147c297127b42c8e1e781_9564cfb8-7e1d-4d48-bd5a-40ce1729bb2d.jpg', 0, 1, NULL, NULL),
(383, 74, '/static/uploads/products/a25349ddcf504533a4ceecc8185c2177_859ef654-0656-4f02-8d04-bead368a6421.jpg', 1, 0, NULL, NULL),
(384, 74, '/static/uploads/products/6a0611c104b94043b11a5d8931558752_1b1e0fe5-39fa-466d-a2c1-297a46bce9c1.jpg', 2, 0, NULL, NULL),
(385, 74, '/static/uploads/products/3acdb5afb49149a9a3a16838363912fc_a3db4c6f-e215-46db-a85e-e818469c8b91.jpg', 3, 0, NULL, NULL),
(386, 74, '/static/uploads/products/d443fdc9f9dc43f9998b26f48cc07d5b_44dcceab-b4bc-46b2-b6b1-ed4903c8709b.jpg', 4, 0, NULL, NULL),
(387, 74, '/static/uploads/products/dfc6d61001eb4c1bb4cc47b5f31b7624_55641a8e-e3d8-4f74-9bb6-da4548d2d03d.jpg', 5, 0, NULL, NULL),
(388, 74, '/static/uploads/products/b27cd776ccd34af5b187a863dd76e3f7_13ee72f8-e685-4d6a-8218-1ebc170c78c3.jpg', 6, 0, NULL, NULL),
(389, 74, '/static/uploads/products/9e2237071157482d9250e37d6ef62861_f31faf62-a4c2-4ca7-82ad-a781cb91ded0.jpg', 7, 0, NULL, NULL),
(390, 74, '/static/uploads/products/ff83e3dafa8c458f8eeb543d735241b2_19013621-1fbc-4ea9-ad4b-cdf99c968c69.jpg', 8, 0, NULL, NULL),
(391, 74, '/static/uploads/products/2fcfb0f5d31742bb9108160882221031_1052b4b8-5342-4ab6-94d7-c4cf13e884e2.jpg', 9, 0, NULL, NULL),
(392, 74, '/static/uploads/products/9b17cd8115374cc0b3e20b85e812a5d9_1e185957-823b-49a8-8724-5c9995f0cafb.jpg', 10, 0, NULL, NULL),
(393, 74, '/static/uploads/products/5761fb5a8d954f29982fa879bc62284f_d8936110-a49b-4c5b-975e-22a31c956b12.jpg', 11, 0, NULL, NULL),
(394, 74, '/static/uploads/products/45257cb66bba47e994b70c40fdeb36d7_0a60e4a5-998f-4f5d-ace3-985a721b8e16.jpg', 12, 0, NULL, NULL),
(395, 74, '/static/uploads/products/7a9c701cc24c4ac8a093fb75a22cbcd5_fc9e37b2-65d8-4c3a-9774-885ef84f25b3.jpg', 13, 0, NULL, NULL),
(396, 74, '/static/uploads/products/0ebea15258144a51b3689c1c34675de0_c883b289-4b76-450f-bca6-43d2d5c8926c.jpg', 14, 0, NULL, NULL),
(397, 74, '/static/uploads/products/8728f167365e42a6abadad6f3885a8b3_3eb34061-0ddc-4318-8738-9d9466596180.jpg', 15, 0, NULL, NULL),
(398, 74, '/static/uploads/products/d0c96cde18194ced919973d35e77a7d9_e35403c2-117a-4a7b-a161-7c4000108182.jpg', 16, 0, NULL, NULL),
(399, 75, '/static/uploads/products/8f3700d765a04a87a4ed193ae5ad9c19_507607f0-23b4-4f9e-85b6-5721e79e9e05.jpg', 0, 1, NULL, NULL),
(400, 75, '/static/uploads/products/14f6cfaf262748f09b89b84704649497_e97fe076-a1d5-4b9c-8fcc-e713c05c5cda.jpg', 1, 0, NULL, NULL),
(401, 75, '/static/uploads/products/7b3c42b51a60408d96922ac0ee565658_b6690f3b-805f-4bce-8fe9-8af243e489cc.jpg', 2, 0, NULL, NULL),
(402, 75, '/static/uploads/products/134bad1b60714d8fa2aca84f790360e5_a8d238c6-2154-40d7-857e-1263da961d6d.jpg', 3, 0, NULL, NULL),
(403, 75, '/static/uploads/products/eb152235f55540299349a5dd325119ef_727ed313-518f-44bd-82d8-d0a56cd7fb8c.jpg', 4, 0, NULL, NULL),
(404, 75, '/static/uploads/products/20f90b52afb84e5cb104752fcd5a4eb1_2fb3bd27-e077-440c-8224-c05d9d5c65b1.jpg', 5, 0, NULL, NULL),
(405, 75, '/static/uploads/products/e847cd67cfad4fcc8fcd259dfe5c4beb_831415d1-32ad-4bfe-91db-d20016b0956a.jpg', 6, 0, NULL, NULL),
(406, 75, '/static/uploads/products/7d8b90f4d2104f428d9dc65f90e13a75_246589b6-3ef9-4960-b205-1ba17e0a9400.jpg', 7, 0, NULL, NULL),
(407, 75, '/static/uploads/products/f78632ce9b6e44959dd8097af0e83580_1b5704d9-b330-43bf-98fb-6f9635ae0efd.jpg', 8, 0, NULL, NULL),
(408, 76, '/static/uploads/products/a9fa010ac74f4c7eb5a9d78355d1512f_1194d82b-0c02-490b-ae3a-944dbe387950.jpg', 0, 1, NULL, NULL);
INSERT INTO `product_images` (`id`, `product_id`, `image_url`, `display_order`, `is_primary`, `alt_text`, `created_at`) VALUES
(409, 76, '/static/uploads/products/1ed9872779464574ba0df2b42e1719d3_6730f696-2dab-4d69-b714-0bc468d203fc.jpg', 1, 0, NULL, NULL),
(410, 76, '/static/uploads/products/aa298fd364304f119f8648fc38d778a9_aa3d0747-9d1d-4f02-bc79-e9631a398f91.jpg', 2, 0, NULL, NULL),
(411, 76, '/static/uploads/products/cc75782853424d5da54a30c01f16923e_ba2f978a-c247-4a4a-81c6-934b5ac9593e.jpg', 3, 0, NULL, NULL),
(412, 76, '/static/uploads/products/20269e6f4ff1426c8ec65d429bac08b1_ee9c84b6-35b5-47e4-b2e4-ec714a008e1a.jpg', 4, 0, NULL, NULL),
(413, 76, '/static/uploads/products/23ece4cd0ddb4581b8a7fdab96df2b57_04166317-7a2d-465f-9d3a-034e5d5c161e.jpg', 5, 0, NULL, NULL),
(414, 76, '/static/uploads/products/58a0cd98b3a24c0e9ab233e36ab7fac5_4dab5741-ccec-468a-bd53-ff53fc21aa8d.jpg', 6, 0, NULL, NULL),
(415, 76, '/static/uploads/products/4ef28737571646f79adf151d2e659d99_72c6f7eb-3261-4890-b25a-22ba909090e0.jpg', 7, 0, NULL, NULL),
(416, 76, '/static/uploads/products/69f57774ede141679b88624f081fabca_32fc877c-c968-44dd-86b0-06745c3ff046.jpg', 8, 0, NULL, NULL),
(417, 76, '/static/uploads/products/233228505ed14930846f2824ee3328b3_bb529afc-ea6f-4ce1-970c-ac52658b0db0.jpg', 9, 0, NULL, NULL),
(418, 76, '/static/uploads/products/f911cabed22b4fc1afe79fcdbf5ee65d_b7eaa001-8181-4125-82ea-e4d31636e465.jpg', 10, 0, NULL, NULL),
(419, 77, '/static/uploads/products/db22821dc83040e691f63285feef6898_d982af1e-c3c5-4a30-a7bf-76fedb0e5644.jpg', 0, 1, NULL, NULL),
(420, 77, '/static/uploads/products/b0a1242d56924ba6b020bdeaf6f401ee_fec4ef79-5f99-4377-baf2-18a7fbef73e1.jpg', 1, 0, NULL, NULL),
(421, 77, '/static/uploads/products/2f4bd930376840bc978019804d971cfc_1a6adff9-a581-4762-b963-9ce36b35af3e.jpg', 2, 0, NULL, NULL),
(422, 77, '/static/uploads/products/4b3c4aefc3eb46868b1ee70f74fb7836_73311f9f-4b30-448b-ab1f-3446bd01b3f3.jpg', 3, 0, NULL, NULL),
(423, 77, '/static/uploads/products/fa8d3c25971649959e667bd11a08dcc8_6652a204-6a7e-4cd1-8cda-f5940e7a86fc.jpg', 4, 0, NULL, NULL),
(424, 77, '/static/uploads/products/815daf0318b146e39b6134982c8c6899_4082fb84-d39b-49a9-baa8-fad5956dc769.jpg', 5, 0, NULL, NULL),
(425, 78, '/static/uploads/products/cd465e7e80ea48e7b4004b23d97e5295_716de079-3063-4713-a315-89afc39dca03.jpg', 0, 1, NULL, NULL),
(426, 78, '/static/uploads/products/f9a1b19d8b1f45ae953eda080a8cd034_5595417b-4136-4c83-912c-2a156aec75d8.jpg', 1, 0, NULL, NULL),
(427, 78, '/static/uploads/products/5f0b1d8fc4d34628b3073357192af446_7c934f5b-be36-4173-97cc-a6f146fc69ff.jpg', 2, 0, NULL, NULL),
(428, 78, '/static/uploads/products/8d63359d67274aaaa9c7918cd7396645_f4c121e2-efcf-4e2e-8fd0-ca24b5cf5ad2.jpg', 3, 0, NULL, NULL),
(429, 78, '/static/uploads/products/ee58f654a3654fef8380c3324a83e59b_7cfb895a-0e0e-4531-a49e-354299d4ca42.jpg', 4, 0, NULL, NULL),
(430, 78, '/static/uploads/products/afdace86470146c98697dba5caf34333_175fa174-a8f6-4291-901d-5512c39c0bf5.jpg', 5, 0, NULL, NULL),
(431, 78, '/static/uploads/products/1d8b8fb6e1814adf9122875edced5aa7_739cbb6f-cc3f-4992-a411-53522d350245.jpg', 6, 0, NULL, NULL),
(432, 78, '/static/uploads/products/dd95fec1b33d4148bb0d4ced30b1a39e_42630ecb-897a-47ca-b6d7-c48fde200283.jpg', 7, 0, NULL, NULL),
(433, 78, '/static/uploads/products/4e03a9ec1da94d5b8d4e389167122a37_3d5f5b2e-2203-413e-a986-69dd05f0aa76.jpg', 8, 0, NULL, NULL),
(434, 79, '/static/uploads/products/050d0c66940943aa9a3afeb44ddfa8b6_09c31e76-26d8-4304-8a86-af4a89e02a10.jpg', 0, 1, NULL, NULL),
(435, 79, '/static/uploads/products/3bc9ec418de545bd874aeb6bf85e1316_e4c60dc0-3c09-42b3-9c71-f1b0bb05008b.jpg', 1, 0, NULL, NULL),
(436, 79, '/static/uploads/products/0afcf233f9274e339759d7a654e0e577_38799640-61a8-4c4d-ad8d-dd7bbb0d712b.jpg', 2, 0, NULL, NULL),
(437, 79, '/static/uploads/products/e22d6f42b6a542d983bb7c6a9249db51_b71325e4-fe66-480e-9efd-fe08196a7f25.jpg', 3, 0, NULL, NULL),
(438, 79, '/static/uploads/products/7218234a63e64462842f52be32a16fa1_b5bfbc83-1419-493d-9f50-01625b996593.jpg', 4, 0, NULL, NULL),
(439, 79, '/static/uploads/products/a05ee73f72f2493ba306767661a98ae8_a009e717-7b9c-497c-bff6-0059ca3e453e.jpg', 5, 0, NULL, NULL),
(440, 79, '/static/uploads/products/5855f7160d944ecaadbc5aef6449773a_cdc457e1-6a06-4630-9b8c-d879a9cc6cb8.jpg', 6, 0, NULL, NULL),
(441, 79, '/static/uploads/products/4871b39d906f42389f5b62fede0319b8_ec0a8449-e635-442c-92ac-c32dc572b2d7.jpg', 7, 0, NULL, NULL),
(442, 79, '/static/uploads/products/63739def2ec64f31b41fc4c6814a1a9f_db015425-7fcd-4326-a37b-12f98975d559.jpg', 8, 0, NULL, NULL),
(443, 79, '/static/uploads/products/1f61436e9fbc4ac09861a16f2ba8db90_b7c6a466-f29e-4c2f-ad88-d350c1a32112.jpg', 9, 0, NULL, NULL),
(444, 79, '/static/uploads/products/da6b73d5b5ad4b9e88b121a8ad44886d_20c87e01-5d0c-47ec-8535-8aaf6f03a055.jpg', 10, 0, NULL, NULL),
(445, 80, '/static/uploads/products/867bedcfdd7242e48ab7cff5b1b115c1_8283c9f9-99e7-4f6b-bea3-ecdba340ef53.jpg', 0, 1, NULL, NULL),
(446, 80, '/static/uploads/products/8c766ff219ea4a6f971ccd40d8f51a65_864e3913-b057-45cc-8521-f097b1238c72.jpg', 1, 0, NULL, NULL),
(447, 80, '/static/uploads/products/baf069076e754984836c38ec9aeaf0ff_c60c1d0b-c847-45df-817c-3a8f5fb89486.jpg', 2, 0, NULL, NULL),
(448, 80, '/static/uploads/products/153312cf938844f8ab1c098b337043cf_9b61fbae-68e3-4048-9953-19527d7f83ee.jpg', 3, 0, NULL, NULL),
(449, 80, '/static/uploads/products/22369544c12f44ebafd6eda567f9e251_5cb545a1-5280-4256-8e2a-cd413dac075f.jpg', 4, 0, NULL, NULL),
(450, 80, '/static/uploads/products/cb96ce0c84cc4e59abe5cd78259d3863_ca7896f8-0c4b-486b-9ccb-4c1a80697e59.jpg', 5, 0, NULL, NULL),
(451, 80, '/static/uploads/products/e4faadf611e54f87a1b78365bc85af96_dbabde79-1286-456e-97a4-06fdb9438d16.jpg', 6, 0, NULL, NULL),
(452, 80, '/static/uploads/products/d0f66806f9ec4cdfb5df4a79aaca2b32_600bbd51-4f60-4d75-8bb9-b5951698edba.jpg', 7, 0, NULL, NULL),
(453, 81, '/static/uploads/products/02586aeb21d6482597bb3754d9d7b46e_196f1397-6999-4c09-afc1-bc5980779586.jpg', 0, 1, NULL, NULL),
(454, 81, '/static/uploads/products/921e2ab8d8ca43d28d87ae0e37a8bbee_48e0ca9f-fdee-4afa-94cc-d4ed55531cae.jpg', 1, 0, NULL, NULL),
(455, 81, '/static/uploads/products/13ad32bbcc344053bc8ff4d4bce3d9e0_0da72f95-a4de-4d20-9062-ae1cdd95eb1b.jpg', 2, 0, NULL, NULL),
(456, 81, '/static/uploads/products/4dc4b286b2ed4c5d83ab53451efa7389_f5ea9c02-fdf3-4dfa-a46a-ea8c2b8ecf5e.jpg', 3, 0, NULL, NULL),
(457, 81, '/static/uploads/products/6015690ad9f34a1c8b89841bbd60bee1_0ea51b6d-0e35-4771-bd3b-a30f80642b5d.jpg', 4, 0, NULL, NULL),
(458, 81, '/static/uploads/products/4bad9fa0ddee41d4896ae5cb0bbb65c1_ed359142-cec0-44c7-b699-bc597daa0163.jpg', 5, 0, NULL, NULL),
(459, 81, '/static/uploads/products/2b3ebefc969f445c823b9277b6c9d75e_f0717664-05ea-470e-b808-2fd08a6deead.jpg', 6, 0, NULL, NULL),
(460, 81, '/static/uploads/products/ef2743e1962344388aa9d6ebc2056d2d_225a5b58-5962-46ac-8917-95ead0edbbbf.jpg', 7, 0, NULL, NULL),
(461, 82, '/static/uploads/products/6c85b3f43d614d15bfd0bbac2a1a82de_a121a081-2fe0-4819-abb8-19be76df09b5.jpg', 0, 1, NULL, NULL),
(462, 82, '/static/uploads/products/b5b59afa10cb443fb94e405673ea5b44_42d7b22d-8944-4ffb-a4ea-4228d0212f0f.jpg', 1, 0, NULL, NULL),
(463, 82, '/static/uploads/products/94ba70245fe040cab2116ab18d42a111_554b7b64-47ca-4a47-b49a-ef8172ead477.jpg', 2, 0, NULL, NULL),
(464, 82, '/static/uploads/products/0e99d43f43304f45838c4deb5be25c66_3e2f2e4d-11fb-45fa-9e2c-49fd91ca187f.jpg', 3, 0, NULL, NULL),
(465, 82, '/static/uploads/products/681e4be5293f481e93fef814f20cabbe_877bf4ad-97be-433c-ab7e-c0aba2945544.jpg', 4, 0, NULL, NULL),
(466, 82, '/static/uploads/products/e41f63f2a85b43aab215360bbdbc1875_1d4b92a8-94d2-44d7-895a-976103c24701.jpg', 5, 0, NULL, NULL),
(467, 82, '/static/uploads/products/303ebb27321d4774b7e5f39c23035a0f_f404c2c6-9f56-4130-b623-5228eeddec8b.jpg', 6, 0, NULL, NULL),
(468, 82, '/static/uploads/products/f0dd9d823a7741a59455f9d4ec4ded0d_6a39c79b-21f9-4be2-9a7b-afd4c9478ed6.jpg', 7, 0, NULL, NULL),
(469, 83, '/static/uploads/products/33d0787fada445dcb5c9455a89500d02_fbd08b57-db59-4d45-82f0-489b053204f2.jpg', 1, 1, NULL, NULL),
(470, 83, '/static/uploads/products/cab3cca3536b41669d80cbe63cdbc788_0613095e-831c-440d-8b46-354ab74de6a0.jpg', 2, 0, NULL, NULL),
(471, 83, '/static/uploads/products/92a898a862f6443b8a32dbda53d510d6_988e0fc8-94e0-4cd7-bc03-71bc6c30b504.jpg', 3, 0, NULL, NULL),
(472, 83, '/static/uploads/products/1b831d2051ca418aba24949905c6a02c_56dd1178-ba41-48f7-b819-03f3080d844e.jpg', 4, 0, NULL, NULL),
(473, 83, '/static/uploads/products/b76b81ce2450488fab732d4209e63f65_8b5d7509-b38a-4832-9ad1-3be8f7336ff8.jpg', 5, 0, NULL, NULL),
(474, 83, '/static/uploads/products/5baf9697f8474471969da3c3248da069_13e20eb2-8937-4a5e-8366-0ce25a4d3e99.jpg', 6, 0, NULL, NULL),
(475, 83, '/static/uploads/products/5ec72f612bec4305851023560fafe4d1_1a1a3a9e-a06f-425a-8b49-d0fd1abea019.jpg', 7, 0, NULL, NULL),
(476, 83, '/static/uploads/products/95f0ae0928ef4176a77187caf62997c2_11d5b389-49f1-4344-b215-ea18d43f1dd4.jpg', 8, 0, NULL, NULL),
(477, 83, '/static/uploads/products/92e7e3ca8f0949c0a466fd46418bc046_02870c27-eaf5-4104-9d28-4eac237142ea.jpg', 0, 0, NULL, NULL),
(478, 84, '/static/uploads/products/51654f2f8def43e49030e2d97fe9670b_d2e138fe-6eb8-479f-8a2d-9731e2d3deca.jpg', 0, 1, NULL, NULL),
(479, 84, '/static/uploads/products/6832013d7db84ab0971a597e681a9d8f_36cd3be3-1fe7-49a7-a2dd-cd008b0dbd0b.jpg', 1, 0, NULL, NULL),
(480, 84, '/static/uploads/products/6945dba5a6c04790ad2d933c75dc70fa_1ab23e90-6629-478d-a4ac-21bbcbf3f8c6.jpg', 2, 0, NULL, NULL),
(481, 84, '/static/uploads/products/94c74f27c90048e99708a9bed9dd8c27_10090be0-9336-4d40-8707-520d7a291b00.jpg', 3, 0, NULL, NULL),
(482, 84, '/static/uploads/products/532818928f544290ad481abceb20573a_cdc98402-44f2-4c52-8cd1-c9cf838957de.jpg', 4, 0, NULL, NULL),
(483, 84, '/static/uploads/products/fd041f4741454acab4d537d4f658bcf4_081bc685-92c8-471a-801e-16c4e3084a70.jpg', 5, 0, NULL, NULL),
(484, 84, '/static/uploads/products/012a86bb762d41e8a4154e00e56fe9e5_e42cc5be-93a0-42e4-8181-ae2cde72713b.jpg', 6, 0, NULL, NULL),
(485, 84, '/static/uploads/products/a7a11943000342fa9c58d3ede9d844b5_dc95fe2e-7573-4d1a-ac8f-40b47f538d0b.jpg', 7, 0, NULL, NULL),
(486, 84, '/static/uploads/products/b2d3e2352a604f61b204f64659c13b44_9966a5fe-bda3-487b-b6df-d642e909b63c.jpg', 8, 0, NULL, NULL),
(487, 84, '/static/uploads/products/11d73c0bba89448380b45e29908be751_df22298b-7e5d-44b1-85e6-577a1824e22a.jpg', 9, 0, NULL, NULL),
(488, 84, '/static/uploads/products/8e1a633c2fe84bed955c94a8537b024d_17909808-ab85-425a-9d26-2b44bd320612.jpg', 10, 0, NULL, NULL),
(489, 85, '/static/uploads/products/2b40a20c23754c80bf1d6523149dd6ae_Screenshot_2025-11-24_100457.png', 0, 1, NULL, NULL),
(490, 85, '/static/uploads/products/3cc1ce633aef47d2a9d102032b7ab25e_Screenshot_2025-11-24_100507.png', 1, 0, NULL, NULL),
(491, 85, '/static/uploads/products/e5fcd36e10e44d32add2557de5f5cf22_Screenshot_2025-11-24_100514.png', 2, 0, NULL, NULL),
(492, 86, '/static/uploads/products/ae516aba58cc448e8a1b27ba79666594_c7ef3c10-b90a-467a-a723-3349050125cc.jpg', 0, 1, NULL, NULL),
(493, 86, '/static/uploads/products/3f151beb5edc4718a5cf8dde70a04844_8babba31-bdf6-4c6a-9cd0-451331df6492.jpg', 1, 0, NULL, NULL),
(494, 86, '/static/uploads/products/fd4900691f184bb5ba58fcf5130e222c_e647b919-47a8-4e5d-9f5e-4b8047a4f826.jpg', 2, 0, NULL, NULL),
(495, 86, '/static/uploads/products/b70f007193ec4e11941284a4eba97c3f_99068d2d-4d8b-4c77-84db-a07e870e1a15.jpg', 3, 0, NULL, NULL),
(496, 86, '/static/uploads/products/3bd587e8700d465dbf407b188152db5f_58b03097-96e0-4a85-8a59-f198f4ea4fc3.jpg', 4, 0, NULL, NULL),
(497, 86, '/static/uploads/products/12fdf5aeeb1749a1bda83c2b091a9875_38b8dc0c-9f2c-46a4-80c3-f73cef811dfe.jpg', 5, 0, NULL, NULL),
(498, 86, '/static/uploads/products/370d5bbb6a774c74914229ea24d93e9e_8113e5d4-c0d7-4fec-ae33-753ce713f9a5.jpg', 6, 0, NULL, NULL),
(499, 87, '/static/uploads/products/9c16e0d20a0246a180fe9a026e0f7951_c706d5ce-e03a-4fcf-ab94-117a491ba203.jpg', 2, 1, NULL, NULL),
(500, 87, '/static/uploads/products/09addd46af6b41d78c8fccfd66f1ad22_77a66f2b-f83f-4990-a542-ae5ff9a5f547.jpg', 3, 0, NULL, NULL),
(501, 87, '/static/uploads/products/4670b855a92a4d18be68e6ed13af0c6f_68fb4e41-dbf6-4727-9555-bb9f7c958d3e.jpg', 1, 0, NULL, NULL),
(502, 87, '/static/uploads/products/41a33000734a49c0b941c1cff93674fa_9f354cd9-83e2-4685-bff5-ceacde006be0.jpg', 4, 0, NULL, NULL),
(503, 87, '/static/uploads/products/d2e5512f1ec34247957b51057235aa3a_6a6dca58-86ae-4b5b-a38d-8206d94b2ae5.jpg', 0, 0, NULL, NULL),
(504, 88, '/static/uploads/products/5b03a79ea505425498a8022b7aa64e19_Screenshot_2025-11-24_104853.png', 0, 1, NULL, NULL),
(505, 88, '/static/uploads/products/56802a9764604875ad2018f4ddd30908_Screenshot_2025-11-24_104904.png', 1, 0, NULL, NULL),
(506, 88, '/static/uploads/products/6b15c61a263e4b58b97bd299fbed0daf_Screenshot_2025-11-24_104915.png', 2, 0, NULL, NULL),
(507, 89, '/static/uploads/products/3a57764df60e44adb74567788f0424be_Screenshot_2025-11-24_105751.png', 0, 1, NULL, NULL),
(508, 89, '/static/uploads/products/fde547dd4362450ba19ca42b12d9f943_Screenshot_2025-11-24_105801.png', 1, 0, NULL, NULL),
(509, 89, '/static/uploads/products/b129457de88e4f5f867d294e60c9fdb2_Screenshot_2025-11-24_105812.png', 2, 0, NULL, NULL),
(510, 90, '/static/uploads/products/998ebf6b0fca4cbea6a33810912e52e4_408d1b34-f681-4ec9-9614-93d2ead914b3.jpg', 0, 1, NULL, NULL),
(511, 90, '/static/uploads/products/43ceba2136be4df6bc94d1f86a0b6ee0_507b73e5-e8cb-4162-93f0-8201d63f94f9.jpg', 1, 0, NULL, NULL),
(512, 90, '/static/uploads/products/896f9b2e804c40d6b3d7069d4a9f361b_9a564e4a-199a-490c-9f55-3c6549a718d9.jpg', 2, 0, NULL, NULL),
(513, 90, '/static/uploads/products/b48692b42cd14c93b1d74ee6a4587c06_b9171ea4-6cd5-4bd0-8e3d-3797e7e62223.jpg', 3, 0, NULL, NULL),
(514, 90, '/static/uploads/products/b51a66e28cd84ff7beecc56c67874929_7f6095aa-f04b-4d3a-8c76-94c7c55eb7e0.jpg', 4, 0, NULL, NULL),
(515, 91, '/static/uploads/products/ea76a46db91b453da24b81b6e8273a71_f7506a38-c63d-4823-aab0-0db21778c17b.jpg', 0, 1, NULL, NULL),
(516, 91, '/static/uploads/products/423fc9d9a1e044ea9170d095cb0ab155_3a45ca52-b22d-47b8-9650-c1ea4186308a.jpg', 1, 0, NULL, NULL),
(517, 91, '/static/uploads/products/08b9dfb5ad074a688a4057952189ebf5_c4a04174-848f-40d1-8992-665d4abcca9a.jpg', 2, 0, NULL, NULL),
(518, 91, '/static/uploads/products/bf60d6ad4f3c4f58b5566b5181d6ac17_c83630d0-d0f4-4a8c-9b1d-a7c6880f9038.jpg', 3, 0, NULL, NULL),
(519, 91, '/static/uploads/products/4c23bba736ea44c9b4315d8a476f4b2e_71c764c0-e8f5-4bbe-81e9-a73dc763f956.jpg', 4, 0, NULL, NULL),
(520, 91, '/static/uploads/products/959decb96ce74f6c8d28534733beb8b4_1ca47217-ac94-4781-a178-50f75bf5f580.jpg', 5, 0, NULL, NULL),
(521, 92, '/static/uploads/products/18fd1fa2cc8f4a73b0f53aaffea1ce81_2ea62138-e6e1-4563-8dd2-8e4a530e4995.jpg', 0, 1, NULL, NULL),
(522, 92, '/static/uploads/products/b516399d9b7b4f579f5bf4856ff71b9a_fd77a4e7-4c88-420f-8eb9-587f6ddad163.jpg', 1, 0, NULL, NULL),
(523, 92, '/static/uploads/products/ed60af6d35cd4f0ab958c7aed3d269e4_b3add71f-aa83-437d-9922-f047ffa767df.jpg', 2, 0, NULL, NULL),
(524, 92, '/static/uploads/products/cd793ad0a15a4981ba31d0bdb47553c6_997cc581-573b-47fd-b9d8-194b327fe591.jpg', 3, 0, NULL, NULL),
(525, 93, '/static/uploads/products/8674f23a809b4be6ab76ee6a4ab1a88e_8632d784-bac6-4b2a-aa15-913043297b20.jpg', 3, 1, NULL, NULL),
(526, 93, '/static/uploads/products/525f9f29c6c949eb93d69eaf494725ae_76862671-2a5b-4af6-9668-5710ad4a100e.jpg', 4, 0, NULL, NULL),
(527, 93, '/static/uploads/products/0673629776de4f0b8fa91c494c66eb74_13995799-f444-4d99-87e9-ed4d4ab7430d.jpg', 5, 0, NULL, NULL),
(528, 93, '/static/uploads/products/e1a97eb5310947e5bae93e7b6de35c33_e78ce512-bbcc-4332-9fc2-e62af4cdcaa3.jpg', 1, 0, NULL, NULL),
(529, 93, '/static/uploads/products/a65720c620c44980b71924f7ae4650ac_510688ae-cca0-417b-a494-379f8b7a8f37.jpg', 2, 0, NULL, NULL),
(530, 93, '/static/uploads/products/18882b79646c4d04b74c80bb5b537619_9d0b5fa7-22cb-45a2-abde-5ceaee1c37b9.jpg', 0, 0, NULL, NULL),
(531, 94, '/static/uploads/products/952ec424744b4d259560daa962f391e8_3bf87d70-02f0-4b0e-9491-4aba855927dc.jpg', 1, 1, NULL, NULL),
(532, 94, '/static/uploads/products/1355f13b7f124075874a773ff47e528c_c4077411-7110-4f82-9585-0dade9ffa5f4.jpg', 3, 0, NULL, NULL),
(533, 94, '/static/uploads/products/c377c303c0f5471685a8ce27771cb6cc_85ccda6b-ce41-42f9-b3b9-1d131083f0b9.jpg', 4, 0, NULL, NULL),
(534, 94, '/static/uploads/products/eb6c7f430db34ccbb0e6c43c21280e0a_81613fbe-0cd2-44dd-9170-8c198b7776fc.jpg', 2, 0, NULL, NULL),
(535, 94, '/static/uploads/products/25f2e510bb3442018aa17644a9af08dc_b53ad824-3666-49e9-a552-f49c5a1dee93.jpg', 5, 0, NULL, NULL),
(536, 94, '/static/uploads/products/90ae7f1b46db45e28af7b580a879cc2d_33d084ad-b997-4755-a80d-530b91e4aa64.jpg', 6, 0, NULL, NULL),
(537, 94, '/static/uploads/products/9bee845cf4ff4153b29cc579adb02de3_d0846925-891c-4d68-ab8e-1aed631b5688.jpg', 0, 0, NULL, NULL),
(538, 95, '/static/uploads/products/e7eb680208c14251b3e28b88a4e4c39b_be1be783-a4a9-4c45-a9a6-84f33a969ae6.jpg', 4, 1, NULL, NULL),
(539, 95, '/static/uploads/products/559d0bb0696a4618a85cdafcd144e3a8_02200ec9-e1a5-4656-b25c-76b438e09887.jpg', 3, 0, NULL, NULL),
(540, 95, '/static/uploads/products/a6492cafd9294aa9a547f070d8a2d8d7_74951bba-776d-4965-8f0c-246bca91560f.jpg', 2, 0, NULL, NULL),
(541, 95, '/static/uploads/products/214d9de96ef448539609b583095ce5be_dc36e6c2-9f61-495a-8f90-ea2219f378ca.jpg', 1, 0, NULL, NULL),
(542, 95, '/static/uploads/products/56779d10565f49ffaa0b62246d172b77_d9ccde28-50de-4635-810d-dffd5df36f83.jpg', 0, 0, NULL, NULL),
(543, 96, '/static/uploads/products/24b8f85d6e9543f285009ac96f277611_5a828f91-9b2b-4ebd-bcbf-cd7947d0d4ef.jpg', 0, 1, NULL, NULL),
(544, 96, '/static/uploads/products/7ddbf0f1b2584d358ff78ca137f3aa5e_24f19ed2-8d26-478e-9045-1e54ca353346.jpg', 1, 0, NULL, NULL),
(545, 96, '/static/uploads/products/854a9f4dd11c450c958ce4923013e884_ski.jpg', 2, 0, NULL, NULL),
(546, 96, '/static/uploads/products/12f6bf802089464da97d510dafe57870_08b10b30-99a5-4537-9a3f-a19759fc22b6.jpg', 3, 0, NULL, NULL),
(547, 96, '/static/uploads/products/d35b14aff3d449dc9dca358b00f1bb1d_Gta.jpg', 4, 0, NULL, NULL);

-- --------------------------------------------------------

--
-- Stand-in structure for view `product_performance`
-- (See below for the actual view)
--
CREATE TABLE `product_performance` (
`id` int(11)
,`name` varchar(200)
,`price` decimal(10,2)
,`stock_quantity` int(11)
,`total_sold` decimal(32,0)
,`total_revenue` decimal(42,2)
,`avg_rating` decimal(14,4)
,`review_count` bigint(21)
);

-- --------------------------------------------------------

--
-- Table structure for table `product_variants`
--

CREATE TABLE `product_variants` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `sku` varchar(100) DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `sale_price` decimal(10,2) DEFAULT NULL,
  `stock_quantity` int(11) DEFAULT 0,
  `image_url` varchar(255) DEFAULT NULL,
  `attributes` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`attributes`)),
  `display_order` int(11) DEFAULT 0,
  `status` enum('active','inactive') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `cost_price` decimal(10,2) DEFAULT NULL COMMENT 'Cost/purchase price for valuation',
  `low_stock_threshold` int(11) DEFAULT 5 COMMENT 'Variant low stock threshold'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `product_variants`
--

INSERT INTO `product_variants` (`id`, `product_id`, `name`, `sku`, `price`, `sale_price`, `stock_quantity`, `image_url`, `attributes`, `display_order`, `status`, `created_at`, `updated_at`, `cost_price`, `low_stock_threshold`) VALUES
(3, 95, 'Lavender', NULL, 299.00, NULL, 100, NULL, NULL, 1, 'active', '2025-11-24 09:17:52', '2025-11-24 10:47:48', NULL, 5),
(4, 95, 'Baby Powder', NULL, 299.00, NULL, 100, NULL, NULL, 2, 'active', '2025-11-24 09:17:52', '2025-11-24 10:48:23', NULL, 5),
(5, 95, 'Bubble Gum', NULL, 299.00, NULL, 100, NULL, NULL, 3, 'active', '2025-11-24 09:17:52', '2025-11-24 10:48:23', NULL, 5);

-- --------------------------------------------------------

--
-- Table structure for table `product_views`
--

CREATE TABLE `product_views` (
  `id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `viewed_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `return_requests`
--

CREATE TABLE `return_requests` (
  `id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `order_item_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `reason` enum('defective','wrong_item','not_as_described','changed_mind','other') NOT NULL,
  `description` text DEFAULT NULL,
  `images` text DEFAULT NULL,
  `status` enum('pending','processing','approved','rejected','cancelled') DEFAULT 'pending',
  `admin_notes` text DEFAULT NULL,
  `refund_amount` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `resolved_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `reviews`
--

CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL CHECK (`rating` >= 1 and `rating` <= 5),
  `comment` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `reviews`
--

INSERT INTO `reviews` (`id`, `user_id`, `product_id`, `rating`, `comment`, `created_at`) VALUES
(5, 4, 7, 5, 'Perfect starter kit for my first aquarium. Everything I needed was included.', '2025-10-22 10:56:35'),
(7, 7, 15, 4, 'iww so yuck', '2025-10-25 01:37:29'),
(9, 6, 19, 2, 'cute, my cat liked it!!', '2025-10-26 19:21:10'),
(11, 16, 26, 5, 'okay naman nagustuhan ng dog ko hehe', '2025-11-20 16:46:15'),
(12, 16, 24, 2, 'miss ko na siya', '2025-11-21 18:30:24');

-- --------------------------------------------------------

--
-- Table structure for table `rider_applications`
--

CREATE TABLE `rider_applications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `vehicle_type` enum('motorcycle','bicycle','car','scooter') NOT NULL,
  `vehicle_plate_number` varchar(20) DEFAULT NULL,
  `vehicle_model` varchar(100) DEFAULT NULL,
  `government_id_path` varchar(255) DEFAULT NULL,
  `vehicle_registration_path` varchar(255) DEFAULT NULL,
  `profile_photo_path` varchar(255) DEFAULT NULL,
  `clearance_path` varchar(255) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `admin_notes` text DEFAULT NULL,
  `training_completed` tinyint(1) DEFAULT 0,
  `training_completed_at` datetime DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `rider_applications`
--

INSERT INTO `rider_applications` (`id`, `user_id`, `vehicle_type`, `vehicle_plate_number`, `vehicle_model`, `government_id_path`, `vehicle_registration_path`, `profile_photo_path`, `clearance_path`, `status`, `admin_notes`, `training_completed`, `training_completed_at`, `submitted_at`, `reviewed_at`, `created_at`, `updated_at`) VALUES
(1, 16, 'motorcycle', '14qyubi', 'Honda click', 'uploads/rider_documents/d4e8fbf238e648d0b8f95adfdce111a3_kylaconservado558_gmail.com_gov_id.jpg', 'uploads/rider_documents/d4e8fbf238e648d0b8f95adfdce111a3_kylaconservado558_gmail.com_vehicle_reg.jpg', 'uploads/rider_profiles/d4e8fbf238e648d0b8f95adfdce111a3_kylaconservado558_gmail.com_profile.jpg', 'uploads/rider_documents/d4e8fbf238e648d0b8f95adfdce111a3_kylaconservado558_gmail.com_clearance.jpg', 'rejected', 'you are not qualify for this position', 0, NULL, '2025-11-03 18:20:12', '2025-11-19 16:15:12', '2025-11-03 18:20:12', '2025-11-19 16:15:12'),
(2, 24, 'motorcycle', '1222', '12222', 'uploads/rider_documents/0554a3c45e8f43a5909ca1e27a381026_cabuhatjohnmark34_gmail.com_gov_id.jpg', 'uploads/rider_documents/0554a3c45e8f43a5909ca1e27a381026_cabuhatjohnmark34_gmail.com_vehicle_reg.jpg', 'uploads/rider_profiles/0554a3c45e8f43a5909ca1e27a381026_cabuhatjohnmark34_gmail.com_profile.jpg', 'uploads/rider_documents/0554a3c45e8f43a5909ca1e27a381026_cabuhatjohnmark34_gmail.com_clearance.jpg', 'pending', NULL, 0, NULL, '2025-11-20 16:03:27', NULL, '2025-11-20 16:03:27', '2025-11-20 16:03:27'),
(3, 26, 'motorcycle', '1234556', 'Ducato', 'uploads/rider_documents/3a2fe160a96e46c18823db64f807cf9c_gigikor973_bablace.com_gov_id.jpg', 'uploads/rider_documents/3a2fe160a96e46c18823db64f807cf9c_gigikor973_bablace.com_vehicle_reg.jpg', 'uploads/rider_profiles/3a2fe160a96e46c18823db64f807cf9c_gigikor973_bablace.com_profile.jpg', 'uploads/rider_documents/3a2fe160a96e46c18823db64f807cf9c_gigikor973_bablace.com_clearance.jpg', 'approved', NULL, 0, NULL, '2025-11-26 13:35:29', '2025-11-26 13:36:29', '2025-11-26 13:35:29', '2025-11-26 13:36:29'),
(5, 28, 'motorcycle', '11111111111', 'Honda', 'uploads/rider_documents/9bcc666d2ba1405fbc95ea4f9e7a5539_xened11223_okcdeals.com_gov_id.jpg', 'uploads/rider_documents/9bcc666d2ba1405fbc95ea4f9e7a5539_xened11223_okcdeals.com_vehicle_reg.jpg', 'uploads/rider_profiles/9bcc666d2ba1405fbc95ea4f9e7a5539_xened11223_okcdeals.com_profile.jpg', 'uploads/rider_documents/9bcc666d2ba1405fbc95ea4f9e7a5539_xened11223_okcdeals.com_clearance.jpg', 'approved', NULL, 0, NULL, '2025-11-26 14:05:45', '2025-11-26 14:06:03', '2025-11-26 14:05:45', '2025-11-26 14:06:03');

-- --------------------------------------------------------

--
-- Table structure for table `rider_availability`
--

CREATE TABLE `rider_availability` (
  `id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `is_online` tinyint(1) NOT NULL,
  `is_available` tinyint(1) NOT NULL,
  `current_location` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`current_location`)),
  `last_seen` datetime DEFAULT NULL,
  `device_info` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`device_info`)),
  `current_order_id` int(11) DEFAULT NULL,
  `current_latitude` decimal(10,8) DEFAULT NULL,
  `current_longitude` decimal(11,8) DEFAULT NULL,
  `last_online` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `rider_availability`
--

INSERT INTO `rider_availability` (`id`, `rider_id`, `is_online`, `is_available`, `current_location`, `last_seen`, `device_info`, `current_order_id`, `current_latitude`, `current_longitude`, `last_online`) VALUES
(1, 4, 1, 1, NULL, NULL, NULL, NULL, 14.23685920, 121.50629850, '2025-11-27 06:09:51'),
(2, 5, 1, 1, NULL, NULL, NULL, NULL, NULL, NULL, '2025-11-02 17:37:45'),
(15, 1, 1, 0, NULL, NULL, NULL, NULL, 14.60910000, 121.02230000, '2025-11-24 21:14:49'),
(16, 16, 1, 0, NULL, NULL, NULL, NULL, 14.60910000, 121.02230000, '2025-11-24 21:16:43'),
(172, 26, 1, 1, NULL, NULL, NULL, NULL, 14.25095070, 121.50629850, '2025-11-26 14:06:40'),
(202, 28, 1, 1, NULL, NULL, NULL, NULL, 14.25372900, 121.50487080, '2025-11-27 22:14:04');

-- --------------------------------------------------------

--
-- Table structure for table `rider_earnings`
--

CREATE TABLE `rider_earnings` (
  `id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `base_fee` decimal(8,2) NOT NULL,
  `distance_fee` decimal(8,2) DEFAULT 0.00,
  `tip_amount` decimal(8,2) DEFAULT 0.00,
  `total_earning` decimal(8,2) NOT NULL,
  `status` enum('pending','paid') DEFAULT 'pending',
  `paid_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `rider_earnings`
--

INSERT INTO `rider_earnings` (`id`, `rider_id`, `order_id`, `base_fee`, `distance_fee`, `tip_amount`, `total_earning`, `status`, `paid_at`, `created_at`) VALUES
(1, 4, 29, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13'),
(2, 4, 33, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13'),
(3, 4, 36, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13'),
(4, 4, 37, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13'),
(5, 4, 47, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13'),
(6, 4, 48, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13'),
(7, 4, 49, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13'),
(8, 4, 51, 3.00, 0.00, 0.00, 3.00, 'pending', NULL, '2025-11-25 03:21:13');

-- --------------------------------------------------------

--
-- Table structure for table `rider_performance`
--

CREATE TABLE `rider_performance` (
  `id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL,
  `feedback` text DEFAULT NULL,
  `delivery_time_minutes` int(11) DEFAULT NULL,
  `rated_by` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ;

-- --------------------------------------------------------

--
-- Table structure for table `sales_analytics`
--

CREATE TABLE `sales_analytics` (
  `id` int(11) NOT NULL,
  `date` date NOT NULL,
  `seller_id` int(11) DEFAULT NULL,
  `total_orders` int(11) DEFAULT 0,
  `total_revenue` decimal(12,2) DEFAULT 0.00,
  `total_items_sold` int(11) DEFAULT 0,
  `avg_order_value` decimal(10,2) DEFAULT 0.00,
  `new_customers` int(11) DEFAULT 0,
  `returning_customers` int(11) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Stand-in structure for view `sales_summary`
-- (See below for the actual view)
--
CREATE TABLE `sales_summary` (
`order_date` date
,`total_orders` bigint(21)
,`total_revenue` decimal(32,2)
,`avg_order_value` decimal(14,6)
);

-- --------------------------------------------------------

--
-- Table structure for table `seller_applications`
--

CREATE TABLE `seller_applications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `business_name` varchar(200) NOT NULL,
  `business_description` text DEFAULT NULL,
  `business_address` text NOT NULL,
  `tax_id` varchar(50) DEFAULT NULL,
  `phone` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `documents` text DEFAULT NULL,
  `status` enum('pending','approved','rejected','under_review') DEFAULT 'pending',
  `admin_notes` text DEFAULT NULL,
  `reviewed_by` int(11) DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `seller_requests`
--

CREATE TABLE `seller_requests` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `business_name` varchar(100) NOT NULL,
  `business_description` text DEFAULT NULL,
  `business_address` text NOT NULL,
  `business_phone` varchar(20) NOT NULL,
  `tax_id` varchar(50) DEFAULT NULL,
  `business_permit` varchar(255) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT 'pending',
  `admin_notes` text DEFAULT NULL,
  `requested_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `reviewed_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `seller_requests`
--

INSERT INTO `seller_requests` (`id`, `user_id`, `business_name`, `business_description`, `business_address`, `business_phone`, `tax_id`, `business_permit`, `status`, `admin_notes`, `requested_at`, `reviewed_at`) VALUES
(1, 6, 'Dog Food in the House oh yeah', 'oh yeah yeah yeah yeha', 'hahahhahhahaha', '111111', '1222223', NULL, 'pending', NULL, '2025-10-24 00:06:26', NULL),
(2, 8, 'Meow Shop', 'Meow Haven Shop is a one-stop destination for cat lovers, offering a wide range of high-quality products and essentials specially curated for feline companions. From nutritious cat food, comfy beds, stylish accessories, to grooming supplies and toys, Meow Haven ensures every cat enjoys comfort, health, and happiness.\r\n\r\nOur shop is dedicated to providing not just products but also care and love for cats. We aim to help cat owners create a better and more enjoyable life for their pets through trusted brands, affordable prices, and excellent customer service. Whether you’re a new cat parent or a long-time cat enthusiast, Cat Haven Shop is your purr-fect partner in giving your cats the best they deserve.', 'Meow Haven Shop\r\n#123 Meow Street, Barangay San Felipe,\r\nQuezon City, Metro Manila, Philippines 1104', '(+63) 912-345-6789', '008-345-921-000', NULL, 'approved', 'hehe dahil cute ka', '2025-10-26 18:58:35', '2025-10-26 18:59:08'),
(3, 9, 'Aww Shop', 'purrfect for your doggie', 'Manila, Cavite', '09224455', '045-345-921-002', NULL, 'pending', NULL, '2025-10-28 15:03:49', NULL),
(4, 1, 'Test Business', 'Test Description', 'Test Address', '1234567890', 'TAX123', 'uploads/business_permits/test.jpg', 'pending', NULL, '2025-10-28 15:18:20', NULL),
(6, 29, 'Dog Finds', 'hehehehehehe', 'hahahahaha', '12121212', '12124335', 'uploads/business_permits/5e5333f2c0bc4224a386364e166ab2d9_rayas56916_aikunkun.com.jpg', 'approved', NULL, '2025-11-26 14:09:15', '2025-11-26 14:09:32');

-- --------------------------------------------------------

--
-- Table structure for table `shipping_providers`
--

CREATE TABLE `shipping_providers` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `base_fee` decimal(10,2) NOT NULL DEFAULT 50.00,
  `per_km_rate` decimal(10,2) NOT NULL DEFAULT 5.00,
  `estimated_delivery_days` int(11) NOT NULL DEFAULT 3,
  `is_active` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `shipping_providers`
--

INSERT INTO `shipping_providers` (`id`, `name`, `base_fee`, `per_km_rate`, `estimated_delivery_days`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'J&T Express', 50.00, 5.00, 3, 1, '2025-10-31 11:27:55', '2025-10-31 11:27:55'),
(2, 'Ninja Van', 60.00, 6.00, 2, 1, '2025-10-31 11:27:55', '2025-10-31 11:27:55'),
(3, 'Lalamove', 70.00, 7.00, 1, 1, '2025-10-31 11:27:55', '2025-10-31 11:27:55'),
(4, 'LBC', 55.00, 5.50, 3, 1, '2025-10-31 11:27:55', '2025-10-31 11:27:55'),
(5, 'JRS Express', 45.00, 4.50, 4, 1, '2025-10-31 11:27:55', '2025-10-31 11:27:55');

-- --------------------------------------------------------

--
-- Table structure for table `system_logs`
--

CREATE TABLE `system_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `details` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `system_logs`
--

INSERT INTO `system_logs` (`id`, `user_id`, `action`, `details`, `ip_address`, `user_agent`, `created_at`) VALUES
(1, 1, 'ADMIN_EXPORT_AUDIT_LOGS', 'Exported 0 audit logs to CSV', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36', '2025-11-10 14:44:49'),
(2, 1, 'ADMIN_EXPORT_AUDIT_LOGS', 'Exported 1 audit logs to CSV', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', '2025-11-12 10:03:21'),
(3, 1, 'ADMIN_APPROVE_SELLER_REQUEST', 'Approved seller request #5 for John Mark Cabuhat', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', '2025-11-19 00:37:30'),
(4, 1, 'ADMIN_REJECT_RIDER_REQUEST', '{\"application_id\": 1, \"applicant\": \"\", \"reason\": \"you are not qualify for this position\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', '2025-11-20 00:15:12'),
(5, 1, 'ADMIN_EXPORT_AUDIT_LOGS', 'Exported 4 audit logs to CSV', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', '2025-11-20 10:36:50'),
(6, 1, 'ADMIN_APPROVE_RIDER_REQUEST', 'Approved rider application #3 for ', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', '2025-11-26 21:36:29'),
(7, 1, 'ADMIN_APPROVE_RIDER_REQUEST', 'Approved rider application #5 for ', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', '2025-11-26 22:06:03'),
(8, 1, 'ADMIN_APPROVE_SELLER_REQUEST', 'Approved seller request #6 for Doggy Shop', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36', '2025-11-26 22:09:32');

-- --------------------------------------------------------

--
-- Table structure for table `system_settings`
--

CREATE TABLE `system_settings` (
  `id` int(11) NOT NULL,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` text DEFAULT NULL,
  `setting_type` varchar(50) DEFAULT 'string',
  `description` text DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `system_settings`
--

INSERT INTO `system_settings` (`id`, `setting_key`, `setting_value`, `setting_type`, `description`, `updated_at`, `created_at`) VALUES
(1, 'site_name', 'PawfectFinds', 'string', 'Website name', '2025-11-10 05:58:02', '2025-11-10 05:57:38'),
(2, 'site_description', 'Your one-stop shop for all pet needs', 'string', 'Website description', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(3, 'admin_email', 'admin@pawfectfinds.com', 'email', 'Administrator email address', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(4, 'support_email', 'support@pawfectfinds.com', 'email', 'Support email address', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(5, 'maintenance_mode', '0', 'boolean', 'Enable/disable maintenance mode', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(6, 'max_products_per_seller', '100', 'integer', 'Maximum products per seller', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(7, 'order_auto_cancel_days', '7', 'integer', 'Days before auto-canceling orders', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(8, 'featured_products_limit', '10', 'integer', 'Number of featured products', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(9, 'default_currency', 'PHP', 'string', 'Default currency', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(10, 'timezone', 'Asia/Manila', 'string', 'System timezone', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(11, 'require_email_verification', '1', 'boolean', 'Require email verification', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(12, 'session_lifetime', '60', 'integer', 'Session lifetime in minutes', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(13, 'max_login_attempts', '5', 'integer', 'Maximum login attempts', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(14, 'enable_cod', '1', 'boolean', 'Enable cash on delivery', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(15, 'enable_card', '0', 'boolean', 'Enable card payments', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(16, 'payment_provider', 'none', 'string', 'Payment provider', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(17, 'payment_public_key', '', 'string', 'Payment provider public key', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(18, 'smtp_host', '', 'string', 'SMTP host', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(19, 'smtp_port', '587', 'integer', 'SMTP port', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(20, 'smtp_tls', '1', 'boolean', 'Use TLS for SMTP', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(21, 'email_from', 'noreply@pawfectfinds.com', 'email', 'Email from address', '2025-11-10 05:57:38', '2025-11-10 05:57:38'),
(22, 'email_theme', 'default', 'string', 'Email template theme', '2025-11-10 05:57:38', '2025-11-10 05:57:38');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text NOT NULL,
  `house_number` varchar(50) DEFAULT NULL,
  `street` varchar(150) DEFAULT NULL,
  `barangay` varchar(100) DEFAULT NULL,
  `role` enum('user','seller','admin','rider') DEFAULT 'user',
  `status` enum('active','inactive','banned') DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `country` varchar(100) NOT NULL DEFAULT 'Philippines',
  `city` varchar(100) NOT NULL DEFAULT 'Manila',
  `province` varchar(100) DEFAULT NULL,
  `postal_code` varchar(20) DEFAULT NULL,
  `id_picture` varchar(255) DEFAULT NULL,
  `profile_image` varchar(255) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT 14.59950000,
  `longitude` decimal(11,8) DEFAULT 120.98420000,
  `is_verified` tinyint(1) DEFAULT 0,
  `verified_at` timestamp NULL DEFAULT NULL,
  `verification_level` enum('none','basic','premium','elite') DEFAULT 'none',
  `payout_method` varchar(50) DEFAULT NULL COMMENT 'bank_transfer, gcash, cash_pickup',
  `bank_name` varchar(100) DEFAULT NULL,
  `account_number` varchar(50) DEFAULT NULL,
  `account_name` varchar(100) DEFAULT NULL,
  `gcash_number` varchar(20) DEFAULT NULL,
  `gcash_name` varchar(100) DEFAULT NULL,
  `pickup_location` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `first_name`, `last_name`, `phone`, `address`, `house_number`, `street`, `barangay`, `role`, `status`, `created_at`, `updated_at`, `country`, `city`, `province`, `postal_code`, `id_picture`, `profile_image`, `latitude`, `longitude`, `is_verified`, `verified_at`, `verification_level`, `payout_method`, `bank_name`, `account_number`, `account_name`, `gcash_number`, `gcash_name`, `pickup_location`) VALUES
(1, 'admin', 'admin@pawfectfinds.com', 'pbkdf2:sha256:260000$EPldXnXRcXdYhNUt$6831a3a1a46e6595478cf13fa05d85cd7fe3849ff25d1719f83cbbde066d0412', 'Admin', 'User', '1234567890', '123 Admin Street, Admin City, AC 12345', NULL, NULL, NULL, 'admin', 'active', '2025-10-22 10:56:35', '2025-10-29 14:50:14', 'Philippines', 'Manila', NULL, NULL, NULL, '/static/uploads/profiles/e328d5a919034a7fb27fb9faf2db90ba_08b10b30-99a5-4537-9a3f-a19759fc22b6.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(4, 'rider1', 'rider1@delivery.com', 'pbkdf2:sha256:260000$YSgQh7tIWyOYTKvz$ca05767ef5ae8c616d10f3302ad29cf2afbe83f848d5c3c878b263382c8b9dc3', 'Alex', 'Rider', '5551112223', '', NULL, NULL, NULL, 'rider', 'active', '2025-10-22 10:56:35', '2025-10-30 04:49:54', 'Philippines', 'Manila', NULL, NULL, NULL, 'uploads/profiles/9f42b1fd9b6549cca4b739fa1ba09373_4.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(5, 'rider2', 'Cocorider@delivery.com', 'pbkdf2:sha256:260000$YSgQh7tIWyOYTKvz$ca05767ef5ae8c616d10f3302ad29cf2afbe83f848d5c3c878b263382c8b9dc3', 'Coco', 'Martin', '5553334445', 'Nasugbu Batangas', NULL, NULL, NULL, 'rider', 'banned', '2025-10-22 10:56:35', '2025-11-27 05:39:46', 'Philippines', 'Manila', NULL, NULL, NULL, 'uploads/profiles/3b79fc216e8146a7a4aa951227786522_5.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(8, 'meowshop', 'meowshop@gmail.com', 'pbkdf2:sha256:260000$46tn3vrShVSjismQ$2d7ffd53a5bdaf4091c22788ecb83315ec54753a88d3ea1a628b856556f40ba4', 'Meow', 'Shop', '098889988', 'newyork city', NULL, NULL, NULL, 'seller', 'active', '2025-10-26 18:55:15', '2025-11-04 05:25:02', 'Philippines', 'Manila', NULL, NULL, NULL, NULL, 14.59950000, 120.98420000, 1, NULL, 'basic', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(16, 'kylaconservado558', 'kylaconservado558@gmail.com', 'scrypt:32768:8:1$poEy5xIdJXnK34iz$ef4092e8c14cb3625fc0a63c1d3e03acc28c4f233b5c3cf40d42cbeb349ec721c6dbc36a8dba1c5e5c569855bab278892415a8952090a909e4b764f4c7be781b', 'Kyla', 'Conservado', '09123456789', '', '43', 'Haha Street', '', 'user', 'active', '2025-10-31 05:19:37', '2025-11-25 09:25:56', 'Philippines', '', 'Rizal', NULL, 'uploads/id_pictures/c09f2983f7764148825cf5ee74285e56_kylaconservado558_gmail.com.jpg', 'uploads/profiles/073cf594c21e445b908d232d7a5dcda3_16.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(24, 'cabuhatjohnmark34', 'cabuhatjohnmark34@gmail.com', 'scrypt:32768:8:1$6qB0W4plyvqRa5RX$35b0e3b7a1ab63e48bd525dbe8f11cdbaf54806d189942244eee59dc32916e35f377ccc2c46ce76f96072a1b05e4002db9d5fba79be4256f8c0077db2bfb32a6', 'John Mark', 'Cabuhat', '09323958886', 'Laguna, Philippines', '12', 'Oliveros', 'Poblacion', 'user', 'active', '2025-11-20 16:03:27', '2025-11-20 16:03:27', 'Philippines', 'Cavinti', 'Laguna', '', 'uploads/id_pictures/be1b4cf4016b46aa9a65181dfb88d0ff_cabuhatjohnmark34_gmail.com.jpg', 'uploads/profiles/6e55023cf2a54ac1b944afdb47259c8b_cabuhatjohnmark34_gmail.com_profile.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(25, 'nisowo3897', 'nisowo3897@moondyal.com', 'scrypt:32768:8:1$dD0RZ2pk73r9ndUS$be9fb264a47977a0cf21f1677b9224f913ef3713f556df55c8429968975e69a31d524d754c04d8724e70c214e1e06babe43e21d9b5f7679cb05c414b73dd935d', 'Joey', 'Askaldo', '09096943848', '24, Bagong Sikat, Poblacion, Cavinti, Laguna, Region IV-A, Philippines', '24', 'Bagong Sikat', 'Poblacion', 'user', 'active', '2025-11-26 12:44:09', '2025-11-26 12:44:09', 'Philippines', 'Cavinti', 'Laguna', '', 'uploads/id_pictures/a93cd4caa33b4801b4275e2eb1f111ce_nisowo3897_moondyal.com.jpg', 'uploads/profiles/2cc8e876a3fd45379d0a518f553d1ee0_nisowo3897_moondyal.com_profile.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(26, 'gigikor973', 'gigikor973@bablace.com', 'scrypt:32768:8:1$6FM2eKEzlTm67Lp4$f426ca38b66ddd697ef7f7342c6ec7c35b2578732ef7f6c79db4f4dcd137f6ff42393ff2a2c4fb1ea574ead28f16c2d92666756d7e0d7a8369affd9dcfde4eff', 'Jeffrey', 'Matigas', '09123456789', '43, Haha Street, Bago, Ibaan, Batangas, Region IV-A, Philippines', '43', 'Haha Street', 'Bago', 'rider', 'active', '2025-11-26 13:35:29', '2025-11-26 14:02:44', 'Philippines', 'Ibaan', 'Batangas', '', 'uploads/id_pictures/6871e796337040be97ea73a395ce1fd8_gigikor973_bablace.com.jpg', 'uploads/profiles/004aedbd81ee47649dfbc3d36bd4a7b7_gigikor973_bablace.com_profile.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(28, 'xened11223', 'xened11223@okcdeals.com', 'scrypt:32768:8:1$DwgYxNyIwZVHSGEA$3e8b5c2801a81ca5bd19588f0f73b4fd87192ee4818a2a7e2fd191227f0b2b7256585d8dcb0897815937244aa2226b1c82d93298fb637833223b08d8fafdc31c', 'Hannah', 'Kim', '092222222', '50, idk, Labac, Cuenca, Batangas, Region IV-A, Philippines', '50', 'idk', 'Labac', 'rider', 'active', '2025-11-26 14:05:45', '2025-11-26 14:06:03', 'Philippines', 'Cuenca', 'Batangas', '', 'uploads/id_pictures/c43b27c1a3714528bfc0890c36a6f29b_xened11223_okcdeals.com.jpg', 'uploads/profiles/35f48d3f0e454673b9474a2684edd35a_xened11223_okcdeals.com_profile.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(29, 'rayas56916', 'rayas56916@aikunkun.com', 'scrypt:32768:8:1$FmubsBU5EZeBQDo9$291f3e51b760fef510a86081af67a8b0bc0dc378dfbec60ac8a884241457bb2f49d37e60d5969a36cfb5e3b780146f4a2c0b5bcb45e4961c9603ee441b6bc99e', 'Doggy', 'Shop', '098888888', '12, Moew, Poblacion, Santo Tomas, La Union, Region I, Philippines', '12', 'Moew', 'Poblacion', 'seller', 'active', '2025-11-26 14:09:15', '2025-11-27 05:39:24', 'Philippines', 'Santo Tomas', 'La Union', '', 'uploads/id_pictures/015688eada8a4ea697fe65dabc8621ef_rayas56916_aikunkun.com.jpg', 'uploads/profiles/5730b314c91142f087c5a3b152f92157_rayas56916_aikunkun.com_profile.jpg', 14.59950000, 120.98420000, 0, NULL, 'none', NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `website_settings`
--

CREATE TABLE `website_settings` (
  `id` int(11) NOT NULL,
  `setting_key` varchar(100) NOT NULL,
  `setting_value` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `website_settings`
--

INSERT INTO `website_settings` (`id`, `setting_key`, `setting_value`, `description`, `updated_at`) VALUES
(1, 'rider_base_fee', '50.00', 'Base delivery fee for riders in PHP', '2025-11-26 20:21:36');

-- --------------------------------------------------------

--
-- Table structure for table `wishlist`
--

CREATE TABLE `wishlist` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `notes` text DEFAULT NULL,
  `priority` enum('low','medium','high') DEFAULT 'medium',
  `notified_when_available` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure for view `product_performance`
--
DROP TABLE IF EXISTS `product_performance`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `product_performance`  AS SELECT `p`.`id` AS `id`, `p`.`name` AS `name`, `p`.`price` AS `price`, `p`.`stock_quantity` AS `stock_quantity`, coalesce(sum(`oi`.`quantity`),0) AS `total_sold`, coalesce(sum(`oi`.`quantity` * `oi`.`price_at_time`),0) AS `total_revenue`, coalesce(avg(`r`.`rating`),0) AS `avg_rating`, count(`r`.`id`) AS `review_count` FROM (((`products` `p` left join `order_items` `oi` on(`p`.`id` = `oi`.`product_id`)) left join `orders` `o` on(`oi`.`order_id` = `o`.`id` and `o`.`status` <> 'cancelled')) left join `reviews` `r` on(`p`.`id` = `r`.`product_id`)) GROUP BY `p`.`id`, `p`.`name`, `p`.`price`, `p`.`stock_quantity` ORDER BY coalesce(sum(`oi`.`quantity`),0) DESC ;

-- --------------------------------------------------------

--
-- Structure for view `sales_summary`
--
DROP TABLE IF EXISTS `sales_summary`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `sales_summary`  AS SELECT cast(`o`.`created_at` as date) AS `order_date`, count(`o`.`id`) AS `total_orders`, sum(`o`.`total_amount`) AS `total_revenue`, avg(`o`.`total_amount`) AS `avg_order_value` FROM `orders` AS `o` WHERE `o`.`status` <> 'cancelled' GROUP BY cast(`o`.`created_at` as date) ORDER BY cast(`o`.`created_at` as date) DESC ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cache_entries`
--
ALTER TABLE `cache_entries`
  ADD PRIMARY KEY (`cache_key`),
  ADD KEY `idx_expires_at` (`expires_at`);

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_product` (`user_id`,`product_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `idx_user` (`user_id`),
  ADD KEY `variant_id` (`variant_id`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `idx_active` (`is_active`),
  ADD KEY `idx_name` (`name`);

--
-- Indexes for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `idx_room_id` (`room_id`),
  ADD KEY `idx_created_at` (`created_at`),
  ADD KEY `idx_is_read` (`is_read`);

--
-- Indexes for table `chat_rooms`
--
ALTER TABLE `chat_rooms`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_updated_at` (`updated_at`),
  ADD KEY `idx_participants` (`participant1_id`,`participant2_id`),
  ADD KEY `idx_conversation_type` (`conversation_type`),
  ADD KEY `idx_related_order` (`related_order_id`),
  ADD KEY `participant2_id` (`participant2_id`);

--
-- Indexes for table `deliveries`
--
ALTER TABLE `deliveries`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_order_rider` (`order_id`,`rider_id`),
  ADD KEY `idx_rider` (`rider_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_assigned` (`assigned_at`);

--
-- Indexes for table `delivery_proofs`
--
ALTER TABLE `delivery_proofs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `rider_id` (`rider_id`);

--
-- Indexes for table `email_templates`
--
ALTER TABLE `email_templates`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `idx_active` (`is_active`),
  ADD KEY `idx_type` (`template_type`),
  ADD KEY `idx_name` (`name`);

--
-- Indexes for table `inventory_transactions`
--
ALTER TABLE `inventory_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`),
  ADD KEY `idx_product_id` (`product_id`),
  ADD KEY `idx_transaction_type` (`transaction_type`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `low_stock_alerts`
--
ALTER TABLE `low_stock_alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_product_id` (`product_id`),
  ADD KEY `idx_seller_id` (`seller_id`),
  ADD KEY `idx_alert_sent` (`alert_sent`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_role` (`user_id`,`role`,`is_read`,`created_at`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `idx_user` (`user_id`),
  ADD KEY `idx_rider` (`rider_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_payment` (`payment_status`),
  ADD KEY `idx_created` (`created_at`),
  ADD KEY `idx_orders_date` (`created_at`),
  ADD KEY `idx_rider_id` (`rider_id`),
  ADD KEY `idx_tracking_number` (`tracking_number`),
  ADD KEY `fk_order_seller` (`seller_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_order` (`order_id`),
  ADD KEY `idx_product` (`product_id`),
  ADD KEY `variant_id` (`variant_id`),
  ADD KEY `fk_order_items_seller` (`seller_id`);

--
-- Indexes for table `order_tracking`
--
ALTER TABLE `order_tracking`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_order_id` (`order_id`),
  ADD KEY `idx_tracking_number` (`tracking_number`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `payout_requests`
--
ALTER TABLE `payout_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `rider_id` (`rider_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `sku` (`sku`),
  ADD KEY `idx_seller` (`seller_id`),
  ADD KEY `idx_category` (`category_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_name` (`name`),
  ADD KEY `idx_price` (`price`),
  ADD KEY `idx_products_price_range` (`price`,`status`),
  ADD KEY `idx_low_stock` (`is_low_stock`),
  ADD KEY `idx_seller_category` (`seller_id`,`category_id`),
  ADD KEY `idx_category_status` (`category_id`,`status`),
  ADD KEY `idx_slug` (`slug`),
  ADD KEY `idx_sku` (`sku`);
ALTER TABLE `products` ADD FULLTEXT KEY `idx_search` (`name`,`description`);

--
-- Indexes for table `product_bundles`
--
ALTER TABLE `product_bundles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_seller_id` (`seller_id`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `product_images`
--
ALTER TABLE `product_images`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `idx_display_order` (`display_order`);

--
-- Indexes for table `product_variants`
--
ALTER TABLE `product_variants`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_product_id` (`product_id`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `product_views`
--
ALTER TABLE `product_views`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_product_id` (`product_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_viewed_at` (`viewed_at`);

--
-- Indexes for table `return_requests`
--
ALTER TABLE `return_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_item_id` (`order_item_id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_order_id` (`order_id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_created_at` (`created_at`);

--
-- Indexes for table `reviews`
--
ALTER TABLE `reviews`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_product_review` (`user_id`,`product_id`),
  ADD KEY `idx_product` (`product_id`),
  ADD KEY `idx_rating` (`rating`),
  ADD KEY `idx_reviews_product_rating` (`product_id`,`rating`);

--
-- Indexes for table `rider_applications`
--
ALTER TABLE `rider_applications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user` (`user_id`),
  ADD KEY `idx_status` (`status`);

--
-- Indexes for table `rider_availability`
--
ALTER TABLE `rider_availability`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `rider_id` (`rider_id`),
  ADD KEY `current_order_id` (`current_order_id`);

--
-- Indexes for table `rider_earnings`
--
ALTER TABLE `rider_earnings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `rider_id` (`rider_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `rider_performance`
--
ALTER TABLE `rider_performance`
  ADD PRIMARY KEY (`id`),
  ADD KEY `rider_id` (`rider_id`),
  ADD KEY `order_id` (`order_id`),
  ADD KEY `rated_by` (`rated_by`);

--
-- Indexes for table `sales_analytics`
--
ALTER TABLE `sales_analytics`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_date_seller` (`date`,`seller_id`),
  ADD KEY `idx_date` (`date`),
  ADD KEY `idx_seller_id` (`seller_id`);

--
-- Indexes for table `seller_applications`
--
ALTER TABLE `seller_applications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `reviewed_by` (`reviewed_by`);

--
-- Indexes for table `seller_requests`
--
ALTER TABLE `seller_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_user` (`user_id`);

--
-- Indexes for table `shipping_providers`
--
ALTER TABLE `shipping_providers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `system_settings`
--
ALTER TABLE `system_settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `setting_key` (`setting_key`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_role` (`role`),
  ADD KEY `idx_status` (`status`),
  ADD KEY `idx_email` (`email`);

--
-- Indexes for table `website_settings`
--
ALTER TABLE `website_settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `setting_key` (`setting_key`);

--
-- Indexes for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_product_wish` (`user_id`,`product_id`),
  ADD KEY `product_id` (`product_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=86;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `chat_rooms`
--
ALTER TABLE `chat_rooms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `deliveries`
--
ALTER TABLE `deliveries`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=41;

--
-- AUTO_INCREMENT for table `delivery_proofs`
--
ALTER TABLE `delivery_proofs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `email_templates`
--
ALTER TABLE `email_templates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `inventory_transactions`
--
ALTER TABLE `inventory_transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `low_stock_alerts`
--
ALTER TABLE `low_stock_alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=136;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=73;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- AUTO_INCREMENT for table `order_tracking`
--
ALTER TABLE `order_tracking`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `payout_requests`
--
ALTER TABLE `payout_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=97;

--
-- AUTO_INCREMENT for table `product_bundles`
--
ALTER TABLE `product_bundles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `product_images`
--
ALTER TABLE `product_images`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=548;

--
-- AUTO_INCREMENT for table `product_variants`
--
ALTER TABLE `product_variants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `product_views`
--
ALTER TABLE `product_views`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `return_requests`
--
ALTER TABLE `return_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `reviews`
--
ALTER TABLE `reviews`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `rider_applications`
--
ALTER TABLE `rider_applications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `rider_availability`
--
ALTER TABLE `rider_availability`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=231;

--
-- AUTO_INCREMENT for table `rider_earnings`
--
ALTER TABLE `rider_earnings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `rider_performance`
--
ALTER TABLE `rider_performance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sales_analytics`
--
ALTER TABLE `sales_analytics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `seller_applications`
--
ALTER TABLE `seller_applications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `seller_requests`
--
ALTER TABLE `seller_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `shipping_providers`
--
ALTER TABLE `shipping_providers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `system_logs`
--
ALTER TABLE `system_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `system_settings`
--
ALTER TABLE `system_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=30;

--
-- AUTO_INCREMENT for table `website_settings`
--
ALTER TABLE `website_settings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `wishlist`
--
ALTER TABLE `wishlist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_ibfk_3` FOREIGN KEY (`variant_id`) REFERENCES `product_variants` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `chat_rooms` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `chat_messages_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `chat_rooms`
--
ALTER TABLE `chat_rooms`
  ADD CONSTRAINT `chat_rooms_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `chat_rooms_ibfk_2` FOREIGN KEY (`participant1_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `chat_rooms_ibfk_3` FOREIGN KEY (`participant2_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `chat_rooms_ibfk_4` FOREIGN KEY (`related_order_id`) REFERENCES `orders` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `deliveries`
--
ALTER TABLE `deliveries`
  ADD CONSTRAINT `deliveries_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `deliveries_ibfk_2` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `delivery_proofs`
--
ALTER TABLE `delivery_proofs`
  ADD CONSTRAINT `delivery_proofs_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  ADD CONSTRAINT `delivery_proofs_ibfk_2` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `email_templates`
--
ALTER TABLE `email_templates`
  ADD CONSTRAINT `email_templates_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `inventory_transactions`
--
ALTER TABLE `inventory_transactions`
  ADD CONSTRAINT `inventory_transactions_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `inventory_transactions_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `low_stock_alerts`
--
ALTER TABLE `low_stock_alerts`
  ADD CONSTRAINT `low_stock_alerts_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `low_stock_alerts_ibfk_2` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `fk_order_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `fk_orders_rider` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `orders_ibfk_4` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `orders_ibfk_5` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `orders_ibfk_6` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `orders_ibfk_7` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `orders_ibfk_8` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `fk_order_items_seller` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

--
-- Constraints for table `order_tracking`
--
ALTER TABLE `order_tracking`
  ADD CONSTRAINT `order_tracking_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `payout_requests`
--
ALTER TABLE `payout_requests`
  ADD CONSTRAINT `payout_requests_ibfk_1` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `products_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`);

--
-- Constraints for table `product_bundles`
--
ALTER TABLE `product_bundles`
  ADD CONSTRAINT `product_bundles_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product_images`
--
ALTER TABLE `product_images`
  ADD CONSTRAINT `product_images_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

--
-- Constraints for table `product_variants`
--
ALTER TABLE `product_variants`
  ADD CONSTRAINT `product_variants_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `product_views`
--
ALTER TABLE `product_views`
  ADD CONSTRAINT `product_views_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `product_views_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `return_requests`
--
ALTER TABLE `return_requests`
  ADD CONSTRAINT `return_requests_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `return_requests_ibfk_2` FOREIGN KEY (`order_item_id`) REFERENCES `order_items` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `return_requests_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `reviews`
--
ALTER TABLE `reviews`
  ADD CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `reviews_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `rider_applications`
--
ALTER TABLE `rider_applications`
  ADD CONSTRAINT `fk_rider_app_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `rider_availability`
--
ALTER TABLE `rider_availability`
  ADD CONSTRAINT `rider_availability_ibfk_1` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `rider_availability_ibfk_2` FOREIGN KEY (`current_order_id`) REFERENCES `orders` (`id`);

--
-- Constraints for table `rider_earnings`
--
ALTER TABLE `rider_earnings`
  ADD CONSTRAINT `rider_earnings_ibfk_1` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `rider_earnings_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`);

--
-- Constraints for table `rider_performance`
--
ALTER TABLE `rider_performance`
  ADD CONSTRAINT `rider_performance_ibfk_1` FOREIGN KEY (`rider_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `rider_performance_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  ADD CONSTRAINT `rider_performance_ibfk_3` FOREIGN KEY (`rated_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `sales_analytics`
--
ALTER TABLE `sales_analytics`
  ADD CONSTRAINT `sales_analytics_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `seller_applications`
--
ALTER TABLE `seller_applications`
  ADD CONSTRAINT `seller_applications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `seller_applications_ibfk_2` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`);

--
-- Constraints for table `seller_requests`
--
ALTER TABLE `seller_requests`
  ADD CONSTRAINT `seller_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `system_logs`
--
ALTER TABLE `system_logs`
  ADD CONSTRAINT `system_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `wishlist`
--
ALTER TABLE `wishlist`
  ADD CONSTRAINT `wishlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `wishlist_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
