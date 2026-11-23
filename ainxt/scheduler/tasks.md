# Scheduler tasks (paste each into Scheduler > New task)

Each runs on the AiNxt server, keeps its history and emails the result. Times are IST and set off the hour to avoid queue delays.

## 1. Catalog watch, daily 06:10
> Run the RuPay 360 workflow "W2 Catalog watch". Use the sources in catalog/sources/registry.json and the jobs in ainxt/web_agent_jobs/. Extract only changed sources. Put every change in the Curator Queue with its source. Email me a list of changed sources and proposals created; say "no changes" if none.

## 2. Daily insight run, daily 07:40
> Run the RuPay 360 workflow "W1 Daily insight run" for the latest complete week. If the Data Quality Sentinel blocks, stop and email why. Otherwise email the top 5 findings (headline, confidence, link) and how many need my verdict.

## 3. Weekly digest, Monday 08:20
> Run "W6 Weekly leadership digest" for the last 7 days and email it.

## 4. Learning loop, Friday 17:40
> Run "W7 Learning loop". Email the scorecard and the proposals created.

## 5. Deal monitor, monthly, 3rd working day 09:10
> Run "W4 Deal monitor" for every deal project in deals/. Email cliff alerts first.

## 6. Proposition impact follow-ups
Created automatically by W3 (D+30 and D+60 after each approved proposition event).
