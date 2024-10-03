-- Table to store exercise tasks with status as 0 (not finished) or 1 (finished)
CREATE TABLE Tasks (
    user_id INT NOT NULL,
    task_id SERIAL PRIMARY KEY,
    exercise VARCHAR(100) NOT NULL,
    reps INT NOT NULL,
    status INT CHECK (status IN (0, 1)) NOT NULL,  -- 0 for not finished, 1 for finished
    assign_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date when task is assigned
);

-- Table to store task transactions
CREATE TABLE Transactions (
    user_id INT NOT NULL,
    task_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    durations FLOAT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
);

-- Insert initial data into Tasks table (with assign_date and status as 0 or 1)
INSERT INTO Tasks (user_id, exercise, reps, status, assign_date) 
VALUES
(1, 'Bicep Curl', 10, 1, '2024-01-10 08:30:00'),  -- Finished, assigned on 2024-01-10
(2, 'Squat', 15, 0, '2024-01-11 09:00:00'),       -- Not finished, assigned on 2024-01-11
(1, 'Push Up', 20, 1, '2024-01-12 10:00:00'),     -- Finished, assigned on 2024-01-12
(3, 'Lunges', 12, 0, '2024-01-13 11:15:00'),      -- Not finished, assigned on 2024-01-13
(2, 'Pull Up', 8, 1, '2024-01-14 12:20:00');      -- Finished, assigned on 2024-01-14

-- Insert initial data into Transactions table
INSERT INTO Transactions (user_id, task_id, durations) 
VALUES
(1, 1, 45.5),  -- User 1, Task 1 (Bicep Curl), took 45.5 seconds
(2, 2, 60.0),  -- User 2, Task 2 (Squat), took 60 seconds
(1, 3, 30.2),  -- User 1, Task 3 (Push Up), took 30.2 seconds
(3, 4, 50.3),  -- User 3, Task 4 (Lunges), took 50.3 seconds
(2, 5, 40.1);  -- User 2, Task 5 (Pull Up), took 40.1 seconds
