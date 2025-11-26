"use strict";

const { CronJob } = require("cron");
const { DateTime } = require("luxon");
const shell = require("shelljs");

const job = new CronJob(
  "0 */1 * * * *", // Run every 1 minutes
  () => {
    console.log(DateTime.local(), "=> Running...");
    shell.exec("python -m py.cron run --symbol=BTC-USDT --interval=1m");
  },
  null,
  true,
  "Asia/Saigon",
  null,
  true // Run handler on init cron job
);
