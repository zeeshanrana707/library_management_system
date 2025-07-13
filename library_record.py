# File: library_record.py

import pandas as pd
import os
from modules.book import Book

class LibraryRecord:
    def __init__(self, filename='data/books.csv'):
        self.filename = filename
        self.df = self._load_records()

    def _load_records(self):
        if os.path.exists(self.filename):
            df = pd.read_csv(self.filename)
            # Fix potential column name mismatch from earlier data
            if 'qty' in df.columns and 'quantity' not in df.columns:
                df['quantity'] = df['qty']
            return df
        return pd.DataFrame(columns=['isbn', 'title', 'author', 'quantity', 'price'])

    def _save_records(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self.df.to_csv(self.filename, index=False)

    def add_book(self, book):
        if self.df['isbn'].astype(str).str.contains(str(book.isbn)).any():
            return False, "Book with this ISBN already exists."
        new_record = pd.DataFrame([book.to_dict()])
        self.df = pd.concat([self.df, new_record], ignore_index=True)
        self._save_records()
        return True, "Book added successfully."

    def get_all_books(self):
        return self.df

    def find_book(self, query, search_by='isbn'):
        if search_by == 'isbn':
            book = self.df[self.df['isbn'].astype(str) == str(query)]
        elif search_by == 'title':
            book = self.df[self.df['title'].str.contains(query, case=False, na=False)]
        elif search_by == 'author':
            book = self.df[self.df['author'].str.contains(query, case=False, na=False)]
        else:
            return None
        if not book.empty:
            return book.iloc[0].to_dict()
        return None

    def update_book(self, isbn, updated_info):
        idx = self.df[self.df['isbn'].astype(str) == str(isbn)].index
        if not idx.empty:
            for key, value in updated_info.items():
                if key in self.df.columns:
                    self.df.loc[idx, key] = value
            self._save_records()
            return True, "Book record updated successfully."
        return False, "Book with this ISBN not found."

    def delete_book(self, isbn):
        initial_len = len(self.df)
        self.df = self.df[self.df['isbn'].astype(str) != str(isbn)]
        if len(self.df) < initial_len:
            self._save_records()
            return True, "Book deleted successfully."
        return False, "Book with this ISBN not found."
