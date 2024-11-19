Create Database PLMSFinal;
use PLMSFinal;
CREATE TABLE User (
    User_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_Name VARCHAR(50),
    Email VARCHAR(50),
    Phone_Number VARCHAR(15),
    User_Type VARCHAR(20),
    Password Varchar(255)
);


CREATE TABLE Parking_Lot (
    Parking_Lot_ID INT PRIMARY KEY AUTO_INCREMENT,
    Available Varchar(10)
)AUTO_INCREMENT = 1;

CREATE TABLE Vehicle (
    Vehicle_ID INT PRIMARY KEY AUTO_INCREMENT,
    Vehicle_Type VARCHAR(50),
    Entry_Time TIMESTAMP,
    License_Plate_Number VARCHAR(20) UNIQUE
);

CREATE TABLE Parking_Transaction (
    Transaction_ID INT PRIMARY KEY AUTO_INCREMENT,
    Vehicle_ID INT ,
    Entry_Time TIMESTAMP,
    Exit_Time TIMESTAMP,
    Payment_Amount Float,
    User_ID INT,
    License_Plate_Number VARCHAR(20) UNIQUE,
    foreign key (License_Plate_Number) REFERENCES Vehicle(License_Plate_Number),
    foreign key (Vehicle_ID) REFERENCES Vehicle(Vehicle_ID),
    foreign key (User_ID)REFERENCES User(User_ID)
);
CREATE TABLE Payment (
    Payment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Transaction_ID INT,
    Payment_Method VARCHAR(20),
    Payment_Amount float,
    Payment_Status VARCHAR(20),
    foreign key (Transaction_ID) REFERENCES Parking_Transaction(Transaction_ID)

);

INSERT into User values(1,'Abhay','abhay@example.com','1234567890','Admin','Abhay');