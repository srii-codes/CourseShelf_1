const { driver } = require("./connection");

const students = [
    ["S001", "Aarav Sharma"], ["S002", "Ananya Iyer"], ["S003", "Rohan Mehta"],
    ["S004", "Ishita Nair"], ["S005", "Rahul Verma"], ["S006", "Sneha Rao"],
    ["S007", "Aditya Kumar"], ["S008", "Meera Singh"], ["S009", "Karan Patel"],
    ["S010", "Diya Menon"], ["S011", "Arjun Reddy"], ["S012", "Nisha Gupta"],
    ["S013", "Vivek Shah"], ["S014", "Priya Nair"], ["S015", "Harsh Jain"],
    ["S016", "Kavya Das"], ["S017", "Manish Rao"], ["S018", "Aditi Kapoor"],
    ["S019", "Rohit Bansal"], ["S020", "Neha Joshi"], ["S021", "Sahil Malhotra"],
    ["S022", "Pooja Agarwal"], ["S023", "Varun Sethi"], ["S024", "Simran Kaur"],
    ["S025", "Akash Mishra"], ["S026", "Tanvi Shah"], ["S027", "Dev Patel"],
    ["S028", "Riya Gupta"], ["S029", "Yash Thakur"], ["S030", "Sneha Kapoor"],
    ["S031", "Kabir Singh"], ["S032", "Maya Iyer"], ["S033", "Aman Verma"],
    ["S034", "Tanya Rao"], ["S035", "Nikhil Jain"], ["S036", "Shreya Menon"],
    ["S037", "Ankit Sharma"], ["S038", "Ira Nair"], ["S039", "Mohit Das"],
    ["S040", "Sanya Gupta"], ["S041", "Rishi Kumar"], ["S042", "Anjali Shah"],
    ["S043", "Dhruv Patel"], ["S044", "Manya Singh"], ["S045", "Rajat Mehta"],
    ["S046", "Kriti Rao"], ["S047", "Aman Joshi"], ["S048", "Nandini Kapoor"],
    ["S049", "Siddharth Jain"], ["S050", "Ayesha Khan"]
];

const books = [
    ["B001", "Database Management Systems", "3rd"],
    ["B002", "Database Management Systems", "4th"],
    ["B003", "Database Management Systems", "5th"],
    ["B004", "Computer Networks", "5th"],
    ["B005", "Computer Networks", "6th"],
    ["B006", "Computer Networks", "7th"],
    ["B007", "Operating System Concepts", "9th"],
    ["B008", "Operating System Concepts", "10th"],
    ["B009", "Operating System Concepts", "11th"],
    ["B010", "Design and Analysis of Algorithms", "3rd"],
    ["B011", "Design and Analysis of Algorithms", "4th"],
    ["B012", "Compiler Design", "2nd"],
    ["B013", "Compiler Design", "3rd"],
    ["B014", "Software Engineering", "8th"],
    ["B015", "Software Engineering", "9th"],
    ["B016", "Artificial Intelligence", "3rd"],
    ["B017", "Artificial Intelligence", "4th"],
    ["B018", "Machine Learning", "1st"],
    ["B019", "Machine Learning", "2nd"],
    ["B020", "Data Structures and Algorithms", "2nd"],
    ["B021", "Data Structures and Algorithms", "3rd"],
    ["B022", "Computer Architecture", "5th"],
    ["B023", "Computer Architecture", "6th"],
    ["B024", "Discrete Mathematics", "7th"],
    ["B025", "Discrete Mathematics", "8th"],
    ["B026", "Probability and Statistics", "4th"],
    ["B027", "Probability and Statistics", "5th"],
    ["B028", "Web Technologies", "1st"],
    ["B029", "Web Technologies", "2nd"],
    ["B030", "Cloud Computing", "1st"],
    ["B031", "Cloud Computing", "2nd"],
    ["B032", "Cyber Security", "2nd"],
    ["B033", "Cyber Security", "3rd"],
    ["B034", "Data Mining", "3rd"],
    ["B035", "Data Mining", "4th"],
    ["B036", "Big Data Analytics", "1st"],
    ["B037", "Big Data Analytics", "2nd"],
    ["B038", "Computer Graphics", "3rd"],
    ["B039", "Computer Graphics", "4th"],
    ["B040", "Distributed Systems", "1st"],
    ["B041", "Distributed Systems", "2nd"],
    ["B042", "Natural Language Processing", "1st"],
    ["B043", "Natural Language Processing", "2nd"],
    ["B044", "Information Security", "3rd"],
    ["B045", "Information Security", "4th"],
    ["B046", "Mobile Computing", "2nd"],
    ["B047", "Mobile Computing", "3rd"],
    ["B048", "Parallel Computing", "1st"],
    ["B049", "Parallel Computing", "2nd"],
    ["B050", "Numerical Methods", "5th"]
];

async function seedDatabase() {
  const session = driver.session();
  try {
    console.log("1. Creating Student nodes...");
    await session.run(`
      UNWIND $students AS student
      MERGE (s:Student {student_id: student[0]})
      SET s.name = student[1]
    `, { students });

    console.log("2. Creating Book nodes...");
    await session.run(`
      UNWIND $books AS book
      MERGE (b:Book {book_id: book[0]})
      SET b.title = book[1], b.edition = book[2]
    `, { books });

    console.log("3. Creating OWNS relationships...");
    await session.run(`
      MATCH (s:Student), (b:Book)
      WHERE toInteger(substring(s.student_id, 1)) = ((toInteger(substring(b.book_id, 1)) - 1) % 50) + 1
      MERGE (s)-[:OWNS]->(b)
    `);

    console.log("4. Creating EDITION_OF relationships...");
    await session.run(`
      MATCH (b1:Book), (b2:Book)
      WHERE b1.title = b2.title AND b1.book_id <> b2.book_id
      MERGE (b1)-[:EDITION_OF]->(b2)
    `);

    console.log("5. Creating LENT_TO relationship chains...");
    await session.run(`
      MATCH (a:Student {student_id: "S001"}), (b:Student {student_id: "S002"})
      MERGE (a)-[r:LENT_TO {book_id: "B001"}]->(b)
      SET r.date = date("2026-09-01"), r.due_date = date("2026-09-15"), r.returned_on = null
    `);
    await session.run(`
      MATCH (a:Student {student_id: "S002"}), (c:Student {student_id: "S003"})
      MERGE (a)-[r:LENT_TO {book_id: "B001"}]->(c)
      SET r.date = date("2026-09-03"), r.due_date = date("2026-09-17"), r.returned_on = null
    `);

    console.log("\nDatabase seeded successfully!");
  } catch (error) {
    console.error("Seeding error:", error);
  } finally {
    await session.close();
    await driver.close();
  }
}

seedDatabase();