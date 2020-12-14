<?php

   class MyDatabase extends SQLite3 {
      function __construct() {
         $this->open('report.db');
       }
   }

   $db = new MyDatabase();

   $queries = ['CREATE TABLE IF NOT EXISTS reports (
                     Device VARCHAR (255) null,
                     VLANS VARCHAR (255) NULL,
                     port VARCHAR (255) NOT NULL,
                     MACS VARCHAR (255) NOT NULL
                  )' ];

     
   // execute the sql commands to create new tables
   foreach ($queries as $sql) {
      $db->exec($sql);
   }

?>