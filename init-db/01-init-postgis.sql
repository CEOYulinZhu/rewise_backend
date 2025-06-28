-- 启用PostGIS扩展
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- 创建UUID扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 验证扩展是否安装成功
SELECT version();
SELECT PostGIS_Version();

-- 显示已安装的扩展
\dx 