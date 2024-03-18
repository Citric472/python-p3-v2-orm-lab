from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in the local dictionary using table row's PK as the dictionary key."""
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """

        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()

    # Update the object id attribute using the primary key value of the new row
        self.id = CURSOR.lastrowid

    # Save the object in the local dictionary using the table row's PK as the dictionary key
        type(self).all[self.id] = self


    @classmethod
    def create(cls, year, summary, employee_id):
       """Initialize a new Review instance and save the object to the database. Return the new instance."""
       review = cls(year, summary, employee_id)
       review.save()
       return review

   
    @classmethod
    def instance_from_db(cls, row):
        """Create a Review instance from a database row."""
        if row:
           review_id, year, summary, employee_id = row
           review = cls(year, summary, employee_id, review_id)
           return review
        else:
             return None

   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance corresponding to the db row retrieved by id."""
        sql = """
            SELECT * FROM reviews
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        else:
             return None


    def update(self):
        """Update the instance's corresponding database record to match its new attribute values."""
        if self.id is not None:
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()
        else:
            raise ValueError("Cannot update review with no id")


    def delete(self):
        """Delete the instance's corresponding database record."""
        if self.id is not None:
            sql = """
                DELETE FROM reviews
                WHERE id = ?
            """
            CURSOR.execute(sql, (self.id,))
            CONN.commit()
            del type(self).all[self.id]  # Remove the instance from the dictionary
            self.id = None  # Reset the id attribute
        else:
            raise ValueError("Cannot delete review with no id")


    @classmethod
    def get_all(cls):
        """Return a list of Review instances for every record in the database."""
        sql = """
            SELECT * FROM reviews
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
   
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, int):
            if year >= 2000:
                self._year = year
            else:
                raise ValueError("Year must be greater than or equal to 2000")
        else:
            raise ValueError("Year must be an integer")
    
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if isinstance(summary, str) and len(summary) > 0:
            self._summary = summary
        else:
            raise ValueError("Summary must be a non-empty string")
    
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        # Perform validation to ensure that the employee ID exists in the employees table
        if not Employee.find_by_id(employee_id):
            raise ValueError("Employee ID does not exist")
        self._employee_id = employee_id