require("dotenv").config();
const neo4j = require("neo4j-driver");

const URI = process.env.NEO4J_URI;
const USERNAME = process.env.NEO4J_USERNAME;
const PASSWORD = process.env.NEO4J_PASSWORD;

if (!URI) {
  console.error("ERROR: NEO4J_URI is undefined. Check your .env file!");
  process.exit(1);
}

const driver = neo4j.driver(URI, neo4j.auth.basic(USERNAME, PASSWORD));

async function testConnection() {
  try {
    await driver.verifyConnectivity();
    console.log("Connected to Neo4j AuraDB successfully!");
  } catch (error) {
    console.error("Neo4j connection failed:");
    console.error(error.message);
  }
}

async function closeDriver() {
  await driver.close();
}

module.exports = {
  driver,
  testConnection,
  closeDriver
};