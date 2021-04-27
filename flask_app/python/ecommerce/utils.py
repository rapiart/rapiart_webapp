from woocommerce import API
from flask import current_app


def woo_check_data(post):
    if post['platform'] == 'woocommerce':
        try:
            wooapi = API(
                url=post['store_url'],
                consumer_key=post['key'],
                consumer_secret=post['secret'],
                wp_api=True,
                version="wc/v3",
                timeout=10,
            )
            if wooapi:
                products = wooapi.get("products").json()
                if isinstance(products, list):
                    return({'status': 'success'})
                else:
                    return({'status': 'error', 'error_number': 1002, 'error': products['message']})
            else:
                return({'status': 'error', 'error_number': 1002, 'error': 'Erro ao conectar com API'})
        except:
            return({'status': 'error', 'error_number': 1002, 'error': 'Erro ao conectar com API'})


def woo_object(user):
    if user.woo_key and user.woo_secret:
        wooapi = API(
            url=user.woo_store_url,
            consumer_key=user.woo_key,
            consumer_secret=current_app.config["cript"].decrypt(user.woo_secret.encode('utf-8')).decode('utf-8'),
            wp_api=True,
            version="wc/v3",
            timeout=10)
        return(wooapi)
    else:
        return None
