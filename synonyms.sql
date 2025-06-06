/*
 Navicat Premium Dump SQL

 Source Server         : 本地flsk
 Source Server Type    : MySQL
 Source Server Version : 80012 (8.0.12)
 Source Host           : 127.0.0.1:3306
 Source Schema         : flask_demo

 Target Server Type    : MySQL
 Target Server Version : 80012 (8.0.12)
 File Encoding         : 65001

 Date: 18/03/2025 11:14:18
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for synonyms
-- ----------------------------
DROP TABLE IF EXISTS `synonyms`;
CREATE TABLE `synonyms`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `word` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `synonym` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `word_synonym`(`word` ASC, `synonym` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of synonyms
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
