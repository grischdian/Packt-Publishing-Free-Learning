"""Module with Interactive shell to deal with a particular ebook."""
from cmd import Cmd

class Prompt(Cmd):
    prompt = 'packt>'
    intro = "Welcome to Packt-Shell! Type ? to list commands"

    def __init__(self, completekey: str="tab",
                 stdin=None,
                 stdout=None,
                 all_books=None,
                 api_client=None,
                 download_directory=None,
                 formats=None,
                 into_folder=False):
        super().__init__(completekey, stdin, stdout)
        self.all_books = all_books
        self.api_client = api_client
        self.download_directory = download_directory
        self.formats = formats
        self.into_folder = into_folder

    def do_exit(self, inp):
        '''exit Packt-Shell! '''
        print("Bye")
        return True

    def do_config_subcommand_test(self, inp):
        return True # Aufgabe: subcommands

    def do_list(self, inp):
        #print("Listing all ebooks '{}'".format(inp)
        for book in self.all_books:
          print(self.all_books.index(book) + 1,  book["title"])

    def do_info(self, inp):
        bookid = int(inp) - 1
        print(self.all_books[bookid])

    def do_get(self, inp):
        bookid = int(inp) - 1
        book = self.all_books[bookid]
        print(self.into_folder)
        print(self.download_directory)
        from downloader import download_products, slugify_product_name
        download_products(self.api_client, self.download_directory, self.formats, [book], into_folder=self.into_folder)

    def help_list(self):
        print("List all ebooks to get ID for Download")