DROP TABLE IF EXISTS tasks;

-- Table to store exercise tasks with status as 0 (not finished) or 1 (finished)
CREATE TABLE Tasks (
    user_id INT NOT NULL,
    task_id SERIAL PRIMARY KEY,
    exercise VARCHAR(100) NOT NULL,
    reps INT NOT NULL,
    status INT CHECK (status IN (0, 1)) NOT NULL,  -- 0 for not finished, 1 for finished
    assign_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date when task is assigned
);

-- Insert initial data into Tasks table (with assign_date and status as 0 or 1)
INSERT INTO Tasks (user_id, exercise, reps, status, assign_date) 
VALUES
-- Day 1
(1, 'Bicep Curl', 12, 1, '2024-10-01 08:05:00'),  -- Finished
(2, 'Bench Press', 8, 0, '2024-10-01 10:00:00'),  -- Not finished
(3, 'Leg Press', 10, 1, '2024-10-01 10:15:00'),   -- Finished
(4, 'Plank', 30, 0, '2024-10-01 11:30:00'),       -- Not finished
(5, 'Tricep Dip', 15, 1, '2024-10-01 12:00:00'),   -- Finished
(6, 'Squat', 20, 1, '2024-10-01 13:00:00'),        -- Finished
(7, 'Pull-Up', 10, 0, '2024-10-01 14:00:00'),      -- Not finished
(8, 'Lunge', 15, 1, '2024-10-01 15:00:00'),        -- Finished
(9, 'Push Up', 25, 0, '2024-10-01 16:00:00'),      -- Not finished
(10, 'Burpee', 20, 1, '2024-10-01 17:00:00'),      -- Finished

-- Day 2
(11, 'Bicep Curl', 14, 0, '2024-10-02 08:05:00'),   -- Not finished
(12, 'Squat', 10, 1, '2024-10-02 10:00:00'),       -- Finished
(13, 'Burpee', 20, 0, '2024-10-02 11:00:00'),      -- Not finished
(14, 'Row', 16, 1, '2024-10-02 12:20:00'),         -- Finished
(15, 'Plank', 60, 0, '2024-10-02 13:00:00'),       -- Not finished
(16, 'Bicep Curl', 8, 1, '2024-10-02 14:00:00'),     -- Finished
(17, 'Bench Press', 12, 0, '2024-10-02 15:30:00'), -- Not finished
(18, 'Lunge', 25, 1, '2024-10-02 16:30:00'),       -- Finished
(19, 'Push Up', 30, 1, '2024-10-02 17:00:00'),     -- Finished
(20, 'Tricep Dip', 10, 0, '2024-10-02 18:00:00'),  -- Not finished

-- Day 3
(21, 'Bicep Curl', 18, 1, '2024-10-03 08:05:00'),  -- Finished
(22, 'Bench Press', 12, 0, '2024-10-03 09:30:00'),-- Not finished
(23, 'Leg Press', 8, 1, '2024-10-03 10:15:00'),   -- Finished
(24, 'Plank', 40, 0, '2024-10-03 11:30:00'),      -- Not finished
(25, 'Tricep Dip', 22, 1, '2024-10-03 12:00:00'), -- Finished
(26, 'Squat', 15, 1, '2024-10-03 13:00:00'),      -- Finished
(27, 'Burpee', 25, 1, '2024-10-03 14:00:00'),     -- Finished
(28, 'Row', 10, 0, '2024-10-03 15:00:00'),        -- Not finished
(29, 'Push Up', 20, 1, '2024-10-03 16:00:00'),    -- Finished
(30, 'Lunge', 30, 0, '2024-10-03 17:00:00'),      -- Not finished

-- Day 4
(31, 'Tricep Dip', 10, 1, '2024-10-04 08:05:00'), -- Finished
(32, 'Squat', 15, 0, '2024-10-04 10:00:00'),      -- Not finished
(33, 'Burpee', 15, 1, '2024-10-04 11:00:00'),     -- Finished
(34, 'Row', 20, 0, '2024-10-04 12:00:00'),        -- Not finished
(35, 'Bicep Curl', 12, 1, '2024-10-04 13:00:00'),   -- Finished
(36, 'Bench Press', 8, 1, '2024-10-04 14:00:00'), -- Finished
(37, 'Leg Press', 20, 0, '2024-10-04 15:00:00'),  -- Not finished
(38, 'Plank', 35, 1, '2024-10-04 16:00:00'),      -- Finished
(39, 'Lunge', 15, 0, '2024-10-04 17:00:00'),      -- Not finished
(40, 'Push Up', 25, 1, '2024-10-04 18:00:00'),    -- Finished

-- Day 5
(41, 'Bicep Curl', 12, 1, '2024-10-05 08:05:00'),  -- Finished
(42, 'Bench Press', 10, 0, '2024-10-05 10:00:00'),-- Not finished
(43, 'Leg Press', 20, 1, '2024-10-05 10:15:00'),  -- Finished
(44, 'Plank', 60, 0, '2024-10-05 11:30:00'),      -- Not finished
(45, 'Tricep Dip', 25, 1, '2024-10-05 12:00:00'),  -- Finished
(46, 'Squat', 18, 1, '2024-10-05 13:00:00'),      -- Finished
(47, 'Burpee', 10, 0, '2024-10-05 14:00:00'),     -- Not finished
(48, 'Row', 15, 1, '2024-10-05 15:00:00'),        -- Finished
(49, 'Push Up', 30, 1, '2024-10-05 16:00:00'),    -- Finished
(50, 'Lunge', 20, 0, '2024-10-05 17:00:00'),      -- Not finished

-- Day 6
(51, 'Bicep Curl', 15, 1, '2024-10-06 08:05:00'),  -- Finished
(52, 'Squat', 20, 0, '2024-10-06 09:30:00'),      -- Not finished
(53, 'Burpee', 25, 1, '2024-10-06 10:15:00'),     -- Finished
(54, 'Row', 10, 1, '2024-10-06 11:00:00'),        -- Finished
(55, 'Plank', 45, 0, '2024-10-06 12:00:00'),      -- Not finished
(56, 'Bench Press', 10, 1, '2024-10-06 13:00:00'),-- Finished
(57, 'Tricep Dip', 20, 1, '2024-10-06 14:30:00'), -- Finished
(58, 'Lunge', 15, 0, '2024-10-06 15:00:00'),      -- Not finished
(59, 'Push Up', 20, 1, '2024-10-06 16:00:00'),    -- Finished
(60, 'Leg Press', 12, 1, '2024-10-06 17:00:00'),   -- Finished

-- Day 7
(61, 'Bicep Curl', 20, 0, '2024-10-07 08:05:00'),   -- Not finished
(62, 'Bench Press', 8, 1, '2024-10-07 10:00:00'),  -- Finished
(63, 'Lunge', 20, 1, '2024-10-07 11:00:00'),       -- Finished
(64, 'Burpee', 15, 1, '2024-10-07 12:00:00'),      -- Finished
(65, 'Tricep Dip', 25, 0, '2024-10-07 13:00:00'),  -- Not finished
(66, 'Plank', 30, 1, '2024-10-07 14:00:00'),       -- Finished
(67, 'Row', 20, 0, '2024-10-07 15:00:00'),         -- Not finished
(68, 'Squat', 15, 1, '2024-10-07 16:00:00'),       -- Finished
(69, 'Push Up', 25, 0, '2024-10-07 17:00:00'),     -- Not finished
(70, 'Leg Press', 10, 1, '2024-10-07 18:00:00'),   -- Finished

-- Day 8
(71, 'Bicep Curl', 15, 1, '2024-10-08 08:05:00'),    -- Finished
(72, 'Squat', 25, 1, '2024-10-08 09:30:00'),       -- Finished
(73, 'Burpee', 20, 1, '2024-10-08 10:15:00'),      -- Finished
(74, 'Row', 15, 0, '2024-10-08 11:00:00'),         -- Not finished
(75, 'Plank', 60, 1, '2024-10-08 12:00:00'),       -- Finished
(76, 'Bench Press', 10, 1, '2024-10-08 13:00:00'), -- Finished
(77, 'Tricep Dip', 18, 1, '2024-10-08 14:30:00'),  -- Finished
(78, 'Lunge', 30, 0, '2024-10-08 15:00:00'),       -- Not finished
(79, 'Push Up', 30, 1, '2024-10-08 16:00:00'),     -- Finished
(80, 'Leg Press', 12, 0, '2024-10-08 17:00:00');    -- Not finished
