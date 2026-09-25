const { driver } = require("./connection");

async function runCRUD() {
  const session = driver.session();
  try {
    console.log("=== 1. CREATE ===");
    const createRes = await session.run(`
      CREATE (s:Student {student_id: "S999", name: "Demo Student"})
      RETURN s.student_id AS id, s.name AS name
    `);
    console.log("Created:", createRes.records[0].get("id"), "-", createRes.records[0].get("name"));

    console.log("\n=== 2. READ ===");
    const readRes = await session.run(`
      MATCH (s:Student {student_id: "S999"})
      RETURN s.student_id AS id, s.name AS name
    `);
    console.log("Read:", readRes.records[0].get("id"), "-", readRes.records[0].get("name"));

    console.log("\n=== 3. UPDATE ===");
    const updateRes = await session.run(`
      MATCH (s:Student {student_id: "S999"})
      SET s.name = "Demo Student Updated"
      RETURN s.student_id AS id, s.name AS name
    `);
    console.log("Updated:", updateRes.records[0].get("id"), "-", updateRes.records[0].get("name"));

    console.log("\n=== 4. DELETE ===");
    await session.run(`
      MATCH (s:Student {student_id: "S999"})
      DELETE s
    `);
    console.log("Deleted student S999 successfully.");

  } catch (error) {
    console.error("CRUD Error:", error);
  } finally {
    await session.close();
  }
}

runCRUD();