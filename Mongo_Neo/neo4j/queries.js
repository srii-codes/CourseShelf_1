const { driver } = require("./connection");

async function runQueries() {
  const session = driver.session();
  try {
    console.log("=========================================");
    console.log("QUERY 1: Find Compatible Alternate Editions");
    console.log("=========================================");
    const q1 = await session.run(`
      MATCH (requested:Book {book_id: "B001"})-[:EDITION_OF]-(alternate:Book)
      RETURN requested.title AS title, 
             requested.edition AS requested_edition, 
             alternate.book_id AS alt_id, 
             alternate.edition AS alt_edition
    `);
    q1.records.forEach(r => {
      console.log(`Requested: ${r.get("title")} (${r.get("requested_edition")})`);
      console.log(`Alternate Available: [${r.get("alt_id")}] ${r.get("alt_edition")} Edition`);
    });

    console.log("\n=========================================");
    console.log("QUERY 2: Trace Current Holder Through Lending Chain");
    console.log("=========================================");
    const q2 = await session.run(`
      MATCH path = (owner:Student)-[r:LENT_TO*1..5]->(holder:Student)
      WHERE ALL(rel IN r WHERE rel.book_id = "B001") AND ALL(rel IN r WHERE rel.returned_on IS NULL)
      RETURN owner.name AS original_owner, holder.name AS current_holder, [node IN nodes(path) | node.name] AS chain
    `);
    q2.records.forEach(r => {
      console.log(`Original Owner: ${r.get("original_owner")}`);
      console.log(`Current Holder: ${r.get("current_holder")}`);
      console.log(`Lending Chain: ${r.get("chain").join(" -> ")}`);
    });

    console.log("\n=========================================");
    console.log("QUERY 3: Find Books Involved in Active Loans");
    console.log("=========================================");
    const q3 = await session.run(`
      MATCH (b:Book)
      OPTIONAL MATCH (owner:Student)-[r:LENT_TO]->(borrower:Student)
      WHERE r.book_id = b.book_id AND r.returned_on IS NULL
      WITH b, count(r) AS active_loans
      WHERE active_loans > 0
      RETURN b.book_id AS book_id, b.title AS title, b.edition AS edition, active_loans
    `);
    q3.records.forEach(r => {
      console.log(`[${r.get("book_id")}] ${r.get("title")} (${r.get("edition")} Ed) - Active Loans: ${r.get("active_loans")}`);
    });

    console.log("\n=========================================");
    console.log("QUERY 4: Find Nearest Owner of an Alternate Edition");
    console.log("=========================================");
    const q4 = await session.run(`
      MATCH (requested:Book {book_id: "B001"})-[:EDITION_OF]-(alternate:Book)
      OPTIONAL MATCH (owner:Student)-[r:LENT_TO]->(borrower:Student)
      WHERE r.book_id = alternate.book_id AND r.returned_on IS NULL
      WITH alternate, count(r) AS active_loans
      WHERE active_loans = 0
      MATCH (student:Student)-[:OWNS]->(alternate)
      RETURN alternate.book_id AS alt_id, alternate.title AS title, alternate.edition AS edition, student.student_id AS owner_id, student.name AS owner_name
    `);
    q4.records.forEach(r => {
      console.log(`Alternate Edition: [${r.get("alt_id")}] ${r.get("title")} (${r.get("edition")})`);
      console.log(`Available Owner: ${r.get("owner_name")} (${r.get("owner_id")})`);
    });

  } catch (error) {
    console.error("Query Execution Error:", error);
  } finally {
    await session.close();
    await driver.close();
  }
}

runQueries();