<!DOCTYPE html>
<html lang="en">


    <head>
        <meta chaset="UTF-8">
        <meta http-equivx="X-UA-Compatible" content="IE=edge">
        <!-- <meta http-equiv="refresh" content="5"> -->
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Modify Username</title>



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
    </head>
    <h3>Modify Username</h3>
    <hr>
    <br>

    <body>

        
    
    <form action="edit_username.php" method="post">
        Current name: <input type="text", name="current_name">
        <br>
        <br>
        <br>

        New Name:<input type="text", name="new_name">
        <br>
        <br>
        <br>

        Password:<input type="password", name="password">
        <br>
        <br>
        <br>
        <input type="submit" class=button font size = -10>

<a href="index.php" class="button"> Home </a> 
</form>
<br> 
<?php 
        $run_flag = 0;
        $current_name = $_POST["current_name"];
        $new_name = $_POST["new_name"];
        $password = $_POST["password"];
        $servername = "localhost"; 
        $username = "default"; 
        $password = "password"; 
        $databasename = "final_project"; 
        
        // CREATE CONNECTION 
        $conn1 = mysqli_connect($servername,  
            $username, $password, $databasename); 
        
        // GET CONNECTION ERRORS 
        if (!$conn1) { 
            die("Connection failed: " . mysqli_connect_error()); 
        } 
        // echo $current_name;
        // echo mysql_real_escape_string($current_name);
        // SQL QUERY 
        $query = "SELECT `rfid` FROM `users` WHERE `first_name` ='" .  $current_name . "';";
        $query2 = "UPDATE `users` SET `first_name` = '" . $new_name . "' WHERE `first_name` = '" .  $current_name . "';";

        

        // $query = "SELECT COUNT(*) FROM users WHERE first_name = 'Devin';"; 

        
        try 
        { 
            // $conn = new PDO( 
            //     "mysql:host=$servername;dbname=$databasename",  
            //     $username, $password); 
        
            // $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); 
            // $stmt = $conn->prepare($query); 
            // // EXECUTING THE QUERY 
            // $stmt->execute(); 
        
            // $r = $stmt->setFetchMode(PDO::FETCH_ASSOC); 
            // // FETCHING DATA FROM DATABASE 
            // $result = $stmt->fetchAll(); 

            
            $result2 = mysqli_query($conn1, $query);
            $totalCount = mysqli_num_rows($result2);
            // echo $_POST["current_name"];

            // echo $result;


            if ($_SERVER['REQUEST_METHOD'] === 'POST')
            {         
                
            if (!empty($_POST["current_name"]) && !empty($_POST["new_name"]) && !empty($_POST["password"]))


            {                
            if ($_POST["password"] == "password"){

                if ($totalCount == 0) {

                echo "<font color = '#FF0000'> Current username does not exist, please input a user that exists.";
            }

            else {
                $stmt = mysqli_query($conn1 , $query2);     
                echo "<font color = '#008000'> Username Modified.";
                 

                }

                
            }

            else {
                echo "<font color = '#FF0000'> Incorrect Password.";

            }

        }


        else {
    
            echo "<font color = '#FF0000'> Empty Field.";
    
    
        }
        }


            foreach ($result as $row)  
            { 
                echo $row["first_name"];
            }
            // OUTPUT DATA OF EACH Row
            
            }

            catch(PDOException $e) { 
                echo "Error: " . $e->getMessage(); 
            } 
    

?>


</body>
</html>