from scrapy_splash import SplashRequest

consent_script = """
    function main(splash)
        assert(splash:go(splash.args.url))
        splash:wait(1)
        splash:runjs('document.querySelector("form.consent-form").submit()')
        splash:wait(3)
        return {
            html = splash:html(),
        }
    end
    """


def get_request(url, parse):
    return SplashRequest(
        url=url,
        callback=parse,
        endpoint='execute',
        dont_filter=True,
        args={'lua_source': consent_script, 'timeout': 10}
    )
