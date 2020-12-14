<?php
   include('database.php');
 
   $sql = "SELECT * from reports";
   $ret = $db->query($sql);
   while($row = $ret->fetchArray(SQLITE3_ASSOC) ) {
      echo($row['Device'] . " | " . $row['VLANS'] . " | " . $row['port']. " | " . $row['MACS'] . "\n");
   }
   
   $db->close();

   //http://localhost/track/list.php

?>