<?php

   class MyDatabase extends SQLite3 {
      function __construct() {
         $this->open('device.db');
       }
   }

   $db = new MyDatabase();

   $queries = ['CREATE TABLE IF NOT EXISTS switches (
                     ip VARCHAR (255) NOT NULL,
                     port VARCHAR (255) NOT NULL,
                     community VARCHAR (255) NOT NULL,
                     version VARCHAR (255) NOT NULL,
                     failed_attempts int default 0 not null,
                     first_probetime VARCHAR (255) NULL,
                     latest_probetime VARCHAR (255) NULL
               )' ];

     
   // execute the sql commands to create new tables
   foreach ($queries as $sql) {
      $db->exec($sql);
   }
?>
