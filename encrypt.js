const fs = require('fs');
const crypto = require('crypto');

// 加密配置
const algorithm = 'aes-256-cbc'; // 使用 AES-256-CBC 算法
const key = crypto.randomBytes(32);   // 256-bit 密钥（生产环境应固定或从安全源获取）
const iv = crypto.randomBytes(16);    // 初始化向量 IV

// 获取环境变量
const envVar = process.env.PROD_EC2_USER || 'default-value';

// 加密函数
function encrypt(text, key, iv) {
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return { encrypted, key: key.toString('hex'), iv: iv.toString('hex') };
}

// 执行加密
const result = encrypt(envVar, key, iv);

// 写入输出文件（可选 JSON 格式）
const output = `
Encrypted Value: ${result.encrypted}
Key (HEX): ${result.key}
IV (HEX): ${result.iv}
`;

fs.writeFileSync('output.txt', output.trim());

console.log(`Encrypted value written to output.txt`);