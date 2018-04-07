import scrapy.cmdline

#Your Spider Class...

def main():
    scrapy.cmdline.execute(['scrapy', 'crawl', 'humans'])

if __name__ == '__main__':
    main()
