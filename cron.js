"use strict";

const { CronJob } = require("cron");
const { DateTime } = require("luxon");
const shell = require("shelljs");

const job = new CronJob(
  "0 */5 * * * *", // Run every 5 minutes
  () => {
    console.log(DateTime.local(), "=> Running...");
    shell.exec("node ./js/fetch.js -p \"ignore\" -s \"BTC\" -i \"1m\" -f 1 -D");
    shell.exec("python ./py/processor.py ./ignore");
    shell.exec("node ./js/robot.js");
  },
  null,
  true,
  "Asia/Saigon",
  null,
  true // Run handler on init cron job
);
