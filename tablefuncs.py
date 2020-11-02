import aiomysql
import os
from datetime import datetime

class table:

    async def get_data(self, args, data=()):
        """Connects to the database and returns data"""
        conn = await aiomysql.connect(
            host=os.environ.get("host"),
            port=3306,
            user=os.environ.get("user"),
            password=os.environ.get("password"),
            db=os.environ.get("database"),
            )

        cur = await conn.cursor()
        await cur.execute(args, data)
        r = await cur.fetchall()
        print(r)
        await cur.close()
        conn.close()
        return r

    async def insert_data(self, args, data=()):
        """Connects to the database and inserts data"""
        conn = await aiomysql.connect(
            host=os.environ.get("host"),
            port=3306,
            user=os.environ.get("user"),
            password=os.environ.get("password"),
            db=os.environ.get("database"),
            )

        cur = await conn.cursor()
        async with conn.cursor() as cur:
            await cur.execute(args, data)
            await conn.commit()

        conn.close()



    async def create_ticket(self, ticket_id, staff_id, name):
        """Creates a ticket or updates the time and last staff to reply to a ticket"""
        await self.create_staff(staff_id, name)
        cursor = await self.get_data("SELECT * FROM `tickets` WHERE `ticket_id` = %s ",(ticket_id, ))
        if not cursor:
            await self.insert_data(
                    "UPDATE staff SET started = started+1, weekly_started = weekly_started+1 WHERE discordid = %s",
                    (staff_id, ))
            print(f"Updated started by for {name}")
            await self.insert_data(
                    "INSERT INTO `tickets`(`ticket_id`, `started_by`, `created_at`) VALUES (%s,%s,%s)",
                    (ticket_id, name, datetime.now()))

            print(f"created ticket: {ticket_id}")
        else:
            await self.insert_data(
                    "UPDATE tickets SET updated_at = null,updated_by = %s WHERE ticket_id =%s",
                    (name, ticket_id))
            print(f"updated ticket: {ticket_id}")

    async def create_staff(self, discord_id, name=""):
        """Checks if a staff member exists, if they don't adds them to the databse"""
        print('trying to add staff')
        cursor = await self.get_data(
                "SELECT * FROM `staff` WHERE `discordid` = %s "
                ,(discord_id, )
                )
        if not cursor:
            print(f"adding staff member {name}")
            await self.insert_data(
                    "INSERT INTO staff(discordid,name) VALUES (%s,%s)",
                    (
                        discord_id,
                        name,
                    )
                    )
        else:
            print('Staff already in DB')



    async def inc_ticket(self, discord_id, name):
        """Increments total tickets for a staff member"""
        cursor = await self.get_data(
            "SELECT * FROM `staff` WHERE `discordid` = %s ",
            (discord_id, ))
        if cursor:
            await self.insert_data(
                    "UPDATE staff SET weekly_tickets = weekly_tickets + 1, total_tickets = total_tickets +1 WHERE discordid = %s",
                    (discord_id, ))
        else:
            await self.create_staff(discord_id, name)
            await self.inc_ticket(discord_id)


    async def reset_weekly_stats(self):
        """Resets weekly stats to 0"""
        await self.insert_data("UPDATE staff SET weekly_tickets = 0")
        await self.insert_data("UPDATE staff SET weekly_Started = 0")

    async def close_ticket(self, ticket_id, discord_id, name):
        """Connects to the database and returns data"""
        await self.inc_ticket(discord_id,name)
        cursor = await self.get_data(
                "SELECT * FROM `tickets` WHERE `ticket_id` = %s ",
                (ticket_id, ))
        if cursor:
            await self.insert_data(
                    "INSERT INTO closed_tickets(ticket_id,started_by,closed_by,created_at) SELECT ticket_id, started_by, %s, created_at FROM tickets WHERE ticket_id =%s",
                    (
                        name,
                        ticket_id,
                    ))
            await self.insert_data(
                                "DELETE FROM tickets WHERE ticket_id = %s",
                                 (ticket_id, ))

    async def get_staff(self, discord_id):
        """Gets the info for a staff member and returns their stats"""
        cursor = await self.get_data(
                "SELECT weekly_tickets,total_tickets,started,weekly_started FROM `staff` WHERE `discordid` = %s ",
                (discord_id, ))
        if cursor:
            return cursor
        else:
            await self.create_staff(discord_id)
            return await self.GetStaff(discord_id)


    async def gen_leaderboard(self):
        """Gets leaderboard info and returns a dict"""
        data = {
              'weekly': [], 
              'overall': [], 
              'weekly_started': [], 
              'started': []
            }

        cursor = await self.get_data(
                "SELECT name,weekly_tickets FROM `staff` ORDER BY weekly_tickets DESC"
            )

        for f in cursor:
            data['weekly'].append(f)

        cursor = await self.get_data(
                "SELECT name,total_tickets FROM `staff` ORDER BY total_tickets DESC"
            )
        for f in cursor:
            data['overall'].append(f)

        cursor = await self.get_data(
                "SELECT name,started FROM `staff` ORDER BY started DESC")
        for f in cursor:
            data['started'].append(f)

        cursor = await self.get_data(
                "SELECT name,weekly_started FROM `staff` ORDER BY weekly_started DESC"
            )
        for f in cursor:
            data['weekly_started'].append(f)

        return data


    async def set_hour_tickets(self, count):
        """Enters the data for tickets from previous hour"""
        await self.insert_data(
                "INSERT INTO `ticket_data`(`Data_ID`, `Num_Tickets`, `Date`) VALUES (0,%s,null)",
                (count, ))

    async def ticket_data(self):
        """Gathers data of tickets taken and returns it"""
        cursor = await self.get_data(
                "SELECT `Num_Tickets` FROM `ticket_data` ORDER BY Date DESC ")
        values = []
        for f in cursor:
            values.append(int(str(f)[1]))

        data = {}
        if values[0]:
            data['last_hour'] = values[0]
            data['overall_tph'] = int(sum(values) / len(values))
        else:
            data['last_hour'] = "n/a"

        if values[1]:
            data['hour_difference'] = values[0] - values[1]
        else:
            data['hour_difference'] = 'More Data Needed'

        if values[23]:
            data['prev_difference'] = values[0] - values[23]
        else:
            data['prev_difference'] = 'More Data Needed'

        if values[23]:
            data['day_avg'] = int(sum(values[0:23]) / 24)
        else:
            data['day_avg'] = 'More Data Needed'

        return data
