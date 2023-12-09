<!DOCTYPE html>
<html lang="en">


    <head>
        <meta chaset="UTF-8">
        <meta http-equivx="X-UA-Compatible" content="IE=edge">
        <meta http-equiv="refresh" content="5">
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Workstation Monitoring System</title>
        <h1> Workstation Monitoring System </h1>


        <style>
            .button {
            background-color:  #00008b;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 10px;
            cursor: pointer;
            }
            .button:hover {
                    background-color: #77C3EC;
                    color: white;
                    }
</style>

    </head>


    <body>

    <!-- <button>Default Button</button> -->
<a href="database_summary.php" class="button">User Analytics</a>

</a>



<a href="edit_username.php" class="button">
        Edit Username
</a>

<a href="remove_user.php" class="button">
        Remove User
</a>

        <br>
        <hr>
        <br>            

        <h3> Workstation Occupancy List </h3>
        <style type="text/css">
            
            table {
            border-collaspe: collapse;
            width: 50%;
            height: 10%;
            color: #00008b;
            font-family: monospace;
            font-size: 25px;
            text-align: center; 
            }

            th{
                background-color:  #00008b;
                color: white;


            }
            th {
              text-align: center;
            }
            tr:nth-child(even) {background-color: #f2f2f2};
        </style>

        <table>
            <tr>
                <th>Workstation</th>
                <th>Status</th>
                <th>Time Remaining</th>
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
        $query = "SELECT workstation, status_,
         remaining_time FROM `ws_occupancy`;"; 
        
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
            

            $WS1_flag = 0;
            $WS2_flag = 0;
            foreach ($result as $row)  
            { 

            

                if ($row["workstation"]  == 1) { //If workstation 1 is being used
                    
                    if ($row["remaining_time"] == 0) {
                        echo "<tr><td>". "Workstation 1"  .  "</td><td> <strong> <font color = #006400>"  . $row["status_"] . "</strong></td><td>" . $row["remaining_time"]  .  "</td><tr>";

                    }

                    else {

                    echo "<tr><td>". "Workstation 1"  .  "</td><td>"  . $row["status_"] . "</td><td>" . $row["remaining_time"]  .  "</td><tr>";
                    $WS1_flag = 1;
                    }
                    
                }

                if ($row["workstation"]  == 2 ) { //If workstation 1 is being used


                    if ($row["remaining_time"] == 0) {
                        echo "<tr><td>". "Workstation 2"  .  "</td><td> <strong> <font color = #006400>"  . $row["status_"] . "</strong></td><td>" . $row["remaining_time"]  .  "</td><tr>";

                    }

                    else {
                    echo "<tr><td>". "Workstation 2"  .  "</td><td>"  . $row["status_"] . "</td><td>" . $row["remaining_time"]  .  "</td><tr>";
                    $WS1_flag = 1;
                    }
                    
                }

            
            }
            echo "</table>";
        } catch(PDOException $e) { 
            echo "Error: " . $e->getMessage(); 
        } 

        
        $conn->close(); 

        echo "<a href=\"database_summary.php\"> <button>Database</button> </a>"
        
        ?>
     <!-- </table> -->


    </body>



</html>

        