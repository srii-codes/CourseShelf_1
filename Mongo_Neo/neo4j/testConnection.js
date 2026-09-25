const { testConnection, closeDriver } = require("./connection");

async function main() {
  await testConnection();
  await closeDriver();
}

main();