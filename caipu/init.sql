-- ============================================
-- 家庭私厨 — 数据库初始化脚本
-- 数据库: caipu_app / MySQL 8.0+
-- 严格对照：需求文档 v3.0 第八章核心数据模型
-- ============================================

CREATE DATABASE IF NOT EXISTS caipu_app
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE caipu_app;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 8.1 用户 (User)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
  id               VARCHAR(64)  NOT NULL PRIMARY KEY COMMENT '用户唯一标识，微信OpenID',
  nickname         VARCHAR(64)  NULL     COMMENT '微信昵称',
  avatar           TEXT         NULL     COMMENT '微信头像URL',
  default_servings INT          NULL     DEFAULT 4   COMMENT '默认用餐人数',
  unit_preference  ENUM('g','jin') NULL DEFAULT 'g'  COMMENT '计量单位：克/斤',
  preferences      JSON         NULL     COMMENT '用户偏好设置（JSON blob）',
  memory_enabled   TINYINT(1)   NULL     DEFAULT 1   COMMENT '配比记忆开关',
  home_tenant_id   VARCHAR(64)  NULL     COMMENT '当前加入的家庭ID',
  created_at       DATETIME     NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  updated_at       DATETIME     NULL     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 8.2 家庭 (Tenant)
-- ============================================
CREATE TABLE IF NOT EXISTS tenants (
  id            VARCHAR(64)  NOT NULL PRIMARY KEY COMMENT '家庭唯一标识',
  name          VARCHAR(64)  NULL     COMMENT '家庭名称',
  owner_id      VARCHAR(64)  NULL     COMMENT '户主userId',
  invite_code   VARCHAR(16)  NULL     COMMENT '邀请码/二维码标识',
  member_count  INT          NULL     DEFAULT 1   COMMENT '成员数',
  created_at    DATETIME     NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at    DATETIME     NULL     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='家庭表';

-- 8.2 家庭成员子表 (TenantMember)
CREATE TABLE IF NOT EXISTS tenant_members (
  id         VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '记录唯一标识',
  tenant_id  VARCHAR(64) NULL     COMMENT '家庭ID',
  user_id    VARCHAR(64) NULL     COMMENT '成员userId',
  role       ENUM('owner','member') NULL DEFAULT 'member' COMMENT '角色',
  joined_at  DATETIME    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='家庭成员表';

-- ============================================
-- 8.3 菜谱 (Recipe)
-- ============================================
CREATE TABLE IF NOT EXISTS recipes (
  id             VARCHAR(64)  NOT NULL PRIMARY KEY COMMENT '菜谱唯一标识',
  name           VARCHAR(128) NOT NULL COMMENT '菜品名称',
  image          TEXT         NULL     COMMENT '菜品图片URL',
  emoji          VARCHAR(8)   NULL     DEFAULT '🍳' COMMENT '菜品emoji',
  tenant_id      VARCHAR(64)  NULL     COMMENT '所属家庭（null=个人私有）',
  owner_id       VARCHAR(64)  NULL     COMMENT '创建者userId',
  status         ENUM('mastered','learning') NULL DEFAULT 'mastered' COMMENT '拿手菜/待学菜谱',
  category       VARCHAR(32)  NULL     COMMENT '分类：肉类/蔬菜/海鲜/素面食/汤类/饮品/甜品',
  difficulty     VARCHAR(8)   NULL     DEFAULT '3'  COMMENT '难度：1-5',
  cook_time      VARCHAR(32)  NULL     COMMENT '制作耗时',
  flavor_tags    JSON         NULL     COMMENT '口味标签数组：咸鲜/麻辣/酸甜/清淡/酱香等',
  meat_type      ENUM('meat','veg','mix') NULL DEFAULT 'mix' COMMENT '荤/素/荤素搭配',
  servings       INT          NULL     DEFAULT 4    COMMENT '当前设定的用餐人数',
  cook_count     INT          NULL     DEFAULT 0    COMMENT '做过次数',
  staple_weight  DECIMAL(8,2) NULL     COMMENT '主食重量（克），null=未设定',
  is_favorited   TINYINT(1)   NULL     DEFAULT 0    COMMENT '是否收藏',
  is_shared      TINYINT(1)   NULL     DEFAULT 0    COMMENT '是否共享到家庭',
  notes          TEXT         NULL     COMMENT '备注/小贴士',
  source         TEXT         NULL     COMMENT '待学来源链接',
  created_at     DATETIME     NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at     DATETIME     NULL     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL,
  FOREIGN KEY (owner_id)  REFERENCES users(id)   ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜谱表';

-- 8.3 菜谱食材子表 (RecipeIngredient)
CREATE TABLE IF NOT EXISTS recipe_ingredients (
  id            VARCHAR(64)  NOT NULL PRIMARY KEY COMMENT '记录唯一标识',
  recipe_id     VARCHAR(64)  NULL     COMMENT '所属菜谱ID',
  ingredient_id VARCHAR(64)  NULL     COMMENT '食材ID',
  amount        DECIMAL(8,2) NULL     COMMENT '用量数值',
  unit          VARCHAR(16)  NULL     COMMENT '单位：克/毫升/个/勺/根',
  is_staple     TINYINT(1)   NULL     DEFAULT 0    COMMENT '是否主食（换算基准）',
  sort_order    INT          NULL     DEFAULT 0    COMMENT '排序序号',
  FOREIGN KEY (recipe_id)     REFERENCES recipes(id)     ON DELETE CASCADE,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜谱食材子表';

-- 8.3 菜谱步骤子表 (RecipeStep)
CREATE TABLE IF NOT EXISTS recipe_steps (
  id          VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '记录唯一标识',
  recipe_id   VARCHAR(64) NULL     COMMENT '所属菜谱ID',
  step_number INT         NULL     COMMENT '步骤序号',
  description TEXT        NULL     COMMENT '步骤文字',
  image       TEXT        NULL     COMMENT '步骤配图URL',
  FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜谱步骤子表';

-- ============================================
-- 8.4 食材库 (Ingredient)
-- ============================================
CREATE TABLE IF NOT EXISTS ingredients (
  id              VARCHAR(64)  NOT NULL PRIMARY KEY COMMENT '食材唯一标识',
  name            VARCHAR(64)  NOT NULL COMMENT '食材名称',
  emoji           VARCHAR(8)   NULL     COMMENT '食材emoji图标',
  image           TEXT         NULL     COMMENT '食材图片URL',
  category1       VARCHAR(32)  NULL     COMMENT '一级分类：畜禽肉类/鲜蔬类/水产海鲜/五谷干货/调味佐料/水果类',
  category2       VARCHAR(32)  NULL     COMMENT '二级分类：猪肉类/绿叶蔬菜/淡水鱼等',
  category3       VARCHAR(32)  NULL     COMMENT '三级分类',
  unit            VARCHAR(16)  NULL     DEFAULT '斤' COMMENT '默认单位',
  storage         ENUM('fridge','freezer','room') NULL DEFAULT 'room' COMMENT '储存方式：冷藏/冷冻/常温',
  shelf_life_days INT          NULL     COMMENT '建议存放天数（冷藏/冷冻类）',
  reference_price DECIMAL(8,2) NULL     COMMENT '参考价格',
  is_system       TINYINT(1)   NULL     DEFAULT 1     COMMENT '是否系统预设（不可删除）',
  created_by      VARCHAR(64)  NULL     COMMENT '自定义食材的创建者userId',
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食材库表';

-- ============================================
-- 8.5 采购记录 (Purchase)
-- ============================================
CREATE TABLE IF NOT EXISTS purchases (
  id             VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '记录唯一标识',
  tenant_id      VARCHAR(64)   NULL     COMMENT '所属家庭（家庭级数据）',
  ingredient_id  VARCHAR(64)   NULL     COMMENT '食材ID',
  price          DECIMAL(8,2)  NULL     COMMENT '单价',
  total_price    DECIMAL(8,2)  NULL     COMMENT '总价',
  quantity       DECIMAL(8,2)  NULL     COMMENT '数量',
  unit           VARCHAR(16)   NULL     COMMENT '购买单位',
  purchase_date  DATE          NULL     COMMENT '采购日期',
  location       VARCHAR(64)   NULL     COMMENT '购买地点',
  note           TEXT          NULL     COMMENT '备注',
  created_by     VARCHAR(64)   NULL     COMMENT '录入者userId',
  created_at     DATETIME      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (tenant_id)     REFERENCES tenants(id)     ON DELETE SET NULL,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by)    REFERENCES users(id)       ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='采购记录表';

-- ============================================
-- 8.6 宴席菜单 (FeastMenu)
-- ============================================
CREATE TABLE IF NOT EXISTS feast_menus (
  id            VARCHAR(64)   NOT NULL PRIMARY KEY COMMENT '菜单唯一标识',
  tenant_id     VARCHAR(64)   NULL     COMMENT '所属家庭',
  name          VARCHAR(128)  NULL     COMMENT '宴席名称',
  template_type VARCHAR(32)   NULL     COMMENT '模板类型：家常小聚/双人简餐/节日正餐/多人宴席/年夜饭',
  scene         VARCHAR(32)   NULL     COMMENT '宴席场景',
  servings      INT           NULL     DEFAULT 6     COMMENT '宴席人数',
  event_date    DATE          NULL     COMMENT '宴席日期',
  total_cost    DECIMAL(10,2) NULL     COMMENT '预估总花费',
  created_by    VARCHAR(64)   NULL     COMMENT '创建者userId',
  created_at    DATETIME      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at    DATETIME      NULL     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间',
  FOREIGN KEY (tenant_id)  REFERENCES tenants(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id)   ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='宴席菜单表';

-- 8.6 宴席菜品子表 (FeastMenuDish)
CREATE TABLE IF NOT EXISTS feast_menu_dishes (
  id             VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '记录唯一标识',
  menu_id        VARCHAR(64) NULL     COMMENT '所属宴席菜单ID',
  recipe_id      VARCHAR(64) NULL     COMMENT '菜品ID',
  feast_category ENUM('cold','hot_meat','hot_veg','soup','staple','dessert') NULL COMMENT '宴席分类：凉菜/热荤/热素/汤羹/主食/甜品',
  sort_order     INT         NULL     DEFAULT 0      COMMENT '上菜排序',
  FOREIGN KEY (menu_id)   REFERENCES feast_menus(id) ON DELETE CASCADE,
  FOREIGN KEY (recipe_id) REFERENCES recipes(id)     ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='宴席菜品子表';

-- ============================================
-- 额外表：点菜规划 (对应3.2点菜模块)
-- ============================================
CREATE TABLE IF NOT EXISTS meal_plans (
  id         VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '记录唯一标识',
  tenant_id  VARCHAR(64) NULL     COMMENT '所属家庭',
  plan_date  DATE        NOT NULL COMMENT '规划日期',
  meal_type  ENUM('breakfast','lunch','dinner') NOT NULL COMMENT '餐段：早餐/午餐/晚餐',
  recipe_id  VARCHAR(64) NULL     COMMENT '菜品ID',
  servings   INT         NULL     DEFAULT 4     COMMENT '用餐人数',
  created_by VARCHAR(64) NULL     COMMENT '创建者userId',
  created_at DATETIME    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
  FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE SET NULL,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='点菜规划表';

-- ============================================
-- 额外表：打卡记录 (对应3.2点菜打卡)
-- ============================================
CREATE TABLE IF NOT EXISTS checkins (
  id           VARCHAR(64) NOT NULL PRIMARY KEY COMMENT '记录唯一标识',
  user_id      VARCHAR(64) NULL     COMMENT '用户ID',
  checkin_date DATE        NOT NULL COMMENT '打卡日期',
  streak_count INT         NULL     DEFAULT 1      COMMENT '连续打卡天数',
  created_at   DATETIME    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '打卡时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='每日打卡记录表';

SET FOREIGN_KEY_CHECKS = 1;
