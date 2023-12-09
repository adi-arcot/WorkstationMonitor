<!DOCTYPE html>
<html lang="en">


    <head>
        <meta chaset="UTF-8">
        <meta http-equivx="X-UA-Compatible" content="IE=edge">
        <meta http-equiv="refresh" content="10">
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Document</title>
    </head>


    <body>
<a href="index.php">
    <button>Home</button>
  </a>
</body>
</html>

<?php 
  $servername = "localhost"; 
  $username = "default"; 
  $password = "password"; 
  $databasename = "final_project"; 
  
  // CREATE CONNECTION 
  $conn = mysqli_connect($servername,  
    $username, $password, $databasename); 
  
  // GET CONNECTION ERRORS 
  if (!$conn) { 
      die("Connection failed: " . mysqli_connect_error()); 
  } 
  
  // SQL QUERY 
  $query = "SELECT first_name, rfid FROM `users`;"; 
  
  try 
  { 
      $conn = new PDO( 
        "mysql:host=$servername;dbname=$databasename",  
        $username, $password); 
  
      $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); 
      $stmt = $conn->prepare($query); 
      // EXECUTING THE QUERY 
      $stmt->execute(); 
  
      $r = $stmt->setFetchMode(PDO::FETCH_ASSOC); 
      // FETCHING DATA FROM DATABASE 
      $result = $stmt->fetchAll(); 
      // OUTPUT DATA OF EACH ROW 
      echo '<table border="0" cellspacing="2" cellpadding="2"> 
      <tr> 
          <td> <font face="Arial">Name</font> </td> 
          <td> <font face="Arial">RFID</font> </td> 
      </tr>';
      
      
      
      foreach ($result as $row)  
      { 

    
          echo  " firstname: ". $row["first_name"] . " - rfid: " .  
            $row["rfid"]. "</br>"; 
        
      }

  } catch(PDOException $e) { 
      echo "Error: " . $e->getMessage(); 
  } 
  
$conn->close(); 
  
?>
