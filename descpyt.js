const fs = require('fs');
const crypto = require('crypto');

// 读取 output.txt 文件
const content = fs.readFileSync('output.txt', 'utf-8');

// 使用正则提取 Encrypted Value, Key 和 IV
const encryptedMatch = content.match(/Encrypted Value: ([0-9a-f]+)/);
const keyMatch = content.match(/Key $HEX$: ([0-9a-f]+)/);
const ivMatch = content.match(/IV $HEX$: ([0-9a-f]+)/);

if (!encryptedMatch || !keyMatch || !ivMatch) {
  console.error('无法从 output.txt 中提取加密信息');
  process.exit(1);
}

const encryptedText = encryptedMatch[1];
const keyHex = keyMatch[1];
const ivHex = ivMatch[1];

// 转换为 Buffer
const key = Buffer.from(keyHex, 'hex');
const iv = Buffer.from(ivHex, 'hex');

// 解密函数
function decrypt(text, key, iv) {
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(text, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

// 执行解密
try {
  const originalText = decrypt(encryptedText, key, iv);
  console.log('✅ 解密成功:');
  console.log('原文内容:', originalText);
} catch (err) {
  console.error('❌ 解密失败:', err.message);
}