DELIMITER //
CREATE PROCEDURE GetUserCredentials(
    IN input_user_id INT,
    IN input_user_type Varchar(20)
)
BEGIN
    -- Retrieve User_Name and Password for the given user ID
    SELECT User_Name, Password
    FROM User
    WHERE User_ID = input_user_id AND User_Type=input_user_type;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetAllOperators()
BEGIN
    SELECT User_ID, User_Name, Email, Phone_Number, User_Type
    FROM User
    WHERE User_Type = 'Operator';
END //

DELIMITER //
CREATE PROCEDURE GetAllAdmins()
BEGIN
    SELECT User_ID, User_Name, Email, Phone_Number, User_Type
    FROM User
    WHERE User_Type = 'Admin';
END //
DELIMITER ;

DELIMITER //

CREATE TRIGGER before_insert_check_id
BEFORE INSERT ON Parking_Lot
FOR EACH ROW
BEGIN
    IF NEW.Parking_Lot_ID > 500 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Parking_Lot_ID cannot exceed 500';
    END IF;
END;//

DELIMITER ;

DELIMITER //

CREATE TRIGGER CalculateParkingCharge
BEFORE INSERT ON Parking_Transaction
FOR EACH ROW
BEGIN
    DECLARE vehicle_type VARCHAR(50);
    DECLARE entry_time TIMESTAMP;
    DECLARE total_hours INT;
    DECLARE base_rate INT;
    DECLARE additional_rate INT;

    -- Fetch vehicle details from the Vehicle table
    SELECT Vehicle_Type, Entry_Time INTO vehicle_type, entry_time
    FROM Vehicle
    WHERE Vehicle_ID = NEW.Vehicle_ID;

    -- Calculate the total parked hours
   
    IF NEW.Exit_Time IS NOT NULL AND entry_time IS NOT NULL THEN
        SET total_hours = TIMESTAMPDIFF(HOUR, entry_time, NEW.Exit_Time);
    ELSE
        SET total_hours = 0; -- or handle the case as needed
    END IF;

        -- Calculate payment based on vehicle type and parked hours
        IF vehicle_type = '2-wheeler' THEN
            SET base_rate = 20;
            SET additional_rate = 10;
        ELSEIF vehicle_type = '4-wheeler' THEN
            SET base_rate = 30;
            SET additional_rate = 20;
        END IF;

        IF total_hours <= 3 THEN
            SET NEW.Payment_Amount = base_rate;
        ELSE
            SET NEW.Payment_Amount = base_rate + CEIL((total_hours - 3) / 3) * additional_rate;
        END IF;
END //

DELIMITER ;
