<!DOCTYPE html>
<html lang="en">


    <head>
        <meta chaset="UTF-8">
        <meta http-equivx="X-UA-Compatible" content="IE=edge">
        <meta http-equiv="refresh" content="10">
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>User Analytics</title>
    </head>
    <h3> User Analytics </h3>

    <body>
        <a href="index.php" class=button>
        Home
        </a>
        <hr>
        <br>
        <style type="text/css">
            
            table {
            border-collaspe: collapse;
            width: 80%;
            color: #00008b;
            font-family: monospace;
            font-size: 25px;
            text-align: right; 
            }

            th{
                background-color: #00008b;
                color: white;


            }
            th {
              text-align: right;
            }
            tr:nth-child(even) {background-color: #f2f2f2};
        </style>

        
        <style>
                    .button {
                    background-color:  #00008b;
                    border: none;
                    color: white;
                    padding: 15px 40px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 18px;
                    margin: 10px 10px;
                    cursor: pointer;
                    }
                    .button:hover {
                    background-color: #77C3EC;
                    color: white;
                    }
        </style>

        <table>
            <tr>
                <th>Name</th>
                <th>RFID</th>
                <th>WS1 Access Count</th>
                <th>WS2 Access Count</th>
                <th>WS1 Overall Time</th>
                <th>WS2 Overall Time</th>

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
        $query = "SELECT first_name, rfid, WS1_noof_access, WS2_noof_access,
         WS1_total_time, WS2_total_time FROM `users`;"; 
        
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
            // OUTPUT DATA OF EACH Row
            
            foreach ($result as $row)  
            { 
                echo "<tr><td>". $row["first_name"] . "</td><td>" . $row["rfid"] . "</td><td>" 
                . $row["WS1_noof_access"] . "</td><td>" . $row["WS2_noof_access"] . "</td><td>" 
                 . $row["WS1_total_time"] . "</td><td>" . $row["WS2_total_time"] . "</td><tr>";
                #echo  " firstname: ". $row["first_name"] . " - rfid: " .  
                #    $row["rfid"]. $row["first_name"] "</br>"; 
            }
            
            echo "</table>";
        } catch(PDOException $e) { 
            echo "Error: " . $e->getMessage(); 
        } 
        
        $conn->close(); 
        
        ?>
     
    </body>

</html>

        