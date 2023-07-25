import pytest
import json
from api.index import app
from urllib.parse import urlencode, urljoin, urlsplit
import time

stores = [
    {
        'route': 'newegg',
        'urls': [
            'https://www.newegg.com/amd-ryzen-5-5600g-ryzen-5-5000-g-series/p/N82E16819113683?Item=N82E16819113683&cm_sp=Homepage_SS-_-P1_19-113-683-_-07162023',
            'https://www.newegg.com/p/054-05WK-00010?Item=9SIANRBJU63766&cm_sp=homepage_sellerrecom-_-9SIANRBJU63766-_-7162023',
            'https://www.newegg.com/p/2M3-0AE0-00011?Item=9SIBKT9JXT0852&cm_sp=homepage_sellerrecom-_-9SIBKT9JXT0852-_-7162023',
            'https://www.newegg.com/dyson-supersonic-styler/p/1EK-004P-00021?Item=9SIADVWJXY0031&cm_sp=Homepage_SS-_-P0_9SIADVWJXY0031-_-07172023',
            'https://www.newegg.com/graphite-black-asus-tuf-gaming-a17-fa706ihr-rs53/p/N82E16834236240?Item=N82E16834236240&cm_sp=Homepage_MKPL-_-P4_34-236-240-_-07172023',
            'https://www.newegg.com/black-fractal-design-focus-2-atx-mid-tower/p/N82E16811352193?Item=N82E16811352193&cm_sp=Homepage_dailydeals-_-P0_11-352-193-_-07172023',
            'https://www.newegg.com/p/05T-000Q-00114?Item=9SIBJAGJJF8294&cm_sp=homepage_sellerrecom-_-9SIBJAGJJF8294-_-7172023',
            'https://www.newegg.com/p/N82E16868105281?Item=N82E16868105281&cm_sp=Homepage_TRENDINGNOW-_-P3_68-105-281-_-07172023',
            'https://www.newegg.com/asrock-radeon-rx-6800-xt-rx6800xt-pgd-16go/p/N82E16814930049?Item=N82E16814930049&cm_sp=Homepage_TRENDINGNOW-_-P2_14-930-049-_-07172023'
            'https://www.newegg.com/amd-ryzen-7-7800x3d-ryzen-7-7000-series/p/N82E16819113793?Item=N82E16819113793&cm_sp=Homepage_TRENDINGNOW-_-P1_19-113-793-_-07172023',
            'https://www.newegg.com/p/0PD-00RS-00003?Item=9SIB38GFP27238&cm_sp=SP-_-1854852-_-TRENDING%20NOW+-_-4-_-9SIB38GFP27238-_--_--_-4',
            'https://www.newegg.com/black-be-quiet-pure-base-atx-micro-atx-mid-tower/p/2AM-0037-00071?Item=9SIA68VB0W1038&cm_sp=SP-_-2019621-_-Pers_HomeBottomSPA-_-8-_-9SIA68VB0W1038-_--_--_-14',
            'https://www.newegg.com/amd-ryzen-9-5950x/p/N82E16819113663?Item=9SIA2W0JWA7462',
            'https://www.newegg.com/amd-ryzen-5-5600-ryzen-5-5000-series/p/N82E16819113736?Item=N82E16819113736',
            'https://www.newegg.com/intel-xeon-silver-4316-lga-4189/p/N82E16819118326?Item=9SIBKT3K114694',
            'https://www.newegg.com/intel-xeon-e3-1225v3-lga-1150/p/N82E16819116910?Item=9SIBKT3K114682'
        ]
    },
    {
        'route': 'amazon',
        'urls': [
            'https://www.amazon.com/AmazonBasics-Pound-Neoprene-Dumbbells-Weights/dp/B01LR5S6HK/?_encoding=UTF8&pd_rd_w=gSNBY&content-id=amzn1.sym.64be5821-f651-4b0b-8dd3-4f9b884f10e5&pf_rd_p=64be5821-f651-4b0b-8dd3-4f9b884f10e5&pf_rd_r=GCBSY8YME6V17RNWC8TJ&pd_rd_wg=SGJCm&pd_rd_r=ae8f15fe-93cb-45c7-9fee-5c454f1c4fa3&ref_=pd_gw_crs_zg_bs_3375251',
            'https://www.amazon.com/Amazon-Basics-63754-19-Inch-Portable/dp/B0B12RQ6RP?ref_=ast_sto_dp&th=1&psc=1',
            'https://www.amazon.com/Amazon-Basics-63763-Tabletop-Portable/dp/B0B12SFRFD?ref_=ast_sto_dp',
            'https://www.amazon.com/Amazon-Basics-Freestanding-Grill-Burner/dp/B0B8R16CS2?ref_=ast_sto_dp&th=1&psc=1',
            'https://www.amazon.com/Amazon-Brand-20-Pocket-Lighted-Rolling/dp/B09RKLMHVW?ref_=ast_sto_dp&th=1&psc=1',
            'https://www.amazon.com/Logitech-Widescreen-Calling-Recording-Desktop/dp/B006JH8T3S?ref_=Oct_d_obs_d_8588809011_0&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B006JH8T3S',
            'https://www.amazon.com/Samsung-LC24F390FHNXZA-24-inch-Monitor-FreeSync/dp/B01CX26WPY?ref_=Oct_d_obs_d_8588809011_1&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B01CX26WPY',
            'https://www.amazon.com/ViewSonic-VX2452MH-Gaming-Monitor-inputs/dp/B00EZSUVHK?ref_=Oct_d_obs_d_8588809011_2&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B00EZSUVHK',
            'https://www.amazon.com/VG278Q-G-Sync-Compatible-Adaptive-Monitor/dp/B074JLD4HZ?ref_=Oct_d_obs_d_8588809011_3&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B074JLD4HZ',
            'https://www.amazon.com/AMD-Ryzen-Processor-Wraith-Cooler/dp/B07B428M7F?ref_=Oct_d_obs_d_8588809011_4&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B07B428M7F',
            'https://www.amazon.com/BenQ-GL2480/dp/B00IKDFL4O?ref_=Oct_d_obs_d_8588809011_5&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B00IKDFL4O',
            'https://www.amazon.com/VANGUARD-Personal-Gaming-Environment-Consoles-Included/dp/B00H0R9DSG?ref_=Oct_d_obs_d_8588809011_6&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B00H0R9DSG',
            'https://www.amazon.com/ASUS-VG248QE-1920x1080-Gaming-Monitor/dp/B00B2HH7G0?ref_=Oct_d_obs_d_8588809011_7&pd_rd_w=Oxo7E&content-id=amzn1.sym.68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_p=68cf20ef-f2f0-42ca-8c87-ad9617594532&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B00B2HH7G0',
            'https://www.amazon.com/ASUS-IPS-Type-GeForce-Gigabit-FX505DV-ES74/dp/B0865SCD6L?ref_=Oct_d_orecs_d_8588809011_1&pd_rd_w=mzcOw&content-id=amzn1.sym.17876e11-0c86-4de6-8819-e1a1ac300756&pf_rd_p=17876e11-0c86-4de6-8819-e1a1ac300756&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B0865SCD6L',
            'https://www.amazon.com/ASUS-VG275Q-Console-FreeSync-Adaptive/dp/B071KHHDNK?ref_=Oct_d_orecs_d_8588809011_2&pd_rd_w=mzcOw&content-id=amzn1.sym.17876e11-0c86-4de6-8819-e1a1ac300756&pf_rd_p=17876e11-0c86-4de6-8819-e1a1ac300756&pf_rd_r=VSJ9KEYXS7TZGRQTTM7Q&pd_rd_wg=nwvU1&pd_rd_r=5a27f8c0-e5d9-4210-8971-1bd7ff8a252a&pd_rd_i=B071KHHDNK'
        ]
    },
    {
        'route': 'craigslist',
        'urls': [
            'https://sfbay.craigslist.org/scz/atq/d/capitola-antique-hand-crank-leather/7643448866.html',
            'https://sfbay.craigslist.org/eby/pts/d/oakland-jeep-cj7-15x8-spoke-wagon/7644518979.html',
            'https://sfbay.craigslist.org/eby/pts/d/oakland-jeep-cj7-15x8-spoke-wagon/7644518979.html',
            'https://sfbay.craigslist.org/sby/pts/d/morgan-hill-nissan-frontier-running/7644512102.html',
            'https://sfbay.craigslist.org/pen/pts/d/daly-city-frs-brz-oem-tail-lights/7636752266.html',
            'https://sfbay.craigslist.org/sby/tls/d/san-jose-empire-true-blue-levels-new/7644622754.html',
            'https://sfbay.craigslist.org/sby/tls/d/san-jose-pc-bondhus-hex-allen-key/7641906384.html',
            'https://sfbay.craigslist.org/sby/tls/d/san-jose-9pc-craftsman-ee-sockets-2/7643894629.html',
            'https://sfbay.craigslist.org/pen/tls/d/south-san-francisco-makita-saw/7637129001.html',
            'https://sfbay.craigslist.org/sby/tls/d/san-jose-craftsman-vv-wrenches-double/7644622041.html',
            'https://sfbay.craigslist.org/eby/tls/d/brentwood-kirby-morgan-superlite-27/7644621934.html',
            'https://sfbay.craigslist.org/sby/tls/d/san-jose-milwaukee-hole-dozer-7piece-bi/7644621569.html',
            'https://sfbay.craigslist.org/nby/tls/d/penngrove-demo-hammer-spade-and-point/7644621098.html',
            'https://sfbay.craigslist.org/sby/tls/d/sunnyvale-kd-drum-brake-calipers-tool/7643915629.html',
            'https://sfbay.craigslist.org/sfc/tls/d/san-francisco-vintage-skilsaw-skill-saw/7637896341.html'
        ]
    },
    {
        'route': 'ebay',
        'urls': [
            'https://www.ebay.com/itm/304808564472?_trkparms=5373%3A0%7C5374%3AFeatured',
        ]
    },
    {
        'route': 'bestbuy',
        'urls': [
            'https://www.bestbuy.com/site/lenovo-legion-tower-5i-gaming-desktop-intel-core-i7-13700f-16gb-memory-nvidia-geforce-rtx-4070-1tb-ssd-storm-grey/6535024.p?skuId=6535024',
            'https://www.bestbuy.com/site/hp-omen-25l-gaming-desktop-intel-core-i3-13100f-8gb-ddr5-memory-nvidia-geforce-gtx-1660-super-512gb-ssd-white/6535732.p?skuId=6535732',
            'https://www.bestbuy.com/site/cyberpowerpc-gamer-master-gaming-desktop-amd-ryzen-7-5700-16gb-memory-nvidia-geforce-rtx-3060-ti-1tb-ssd-black/6533263.p?skuId=6533263',
            'https://www.bestbuy.com/site/hp-omen-25l-gaming-desktop-intel-core-i5-13400f-16gb-ddr5-memory-nvidia-geforce-rtx-3060-1tb-ssd-white/6535734.p?skuId=6535734',
            'https://www.bestbuy.com/site/ibuypower-y40-gaming-desktop-intel-core-i7-13700kf-32gb-memory-nvidia-geforce-rtx-4070-12gb-1tb-nvme-ssd-black/6541529.p?skuId=6541529',
            'https://www.bestbuy.com/site/cyberpowerpc-gamer-supreme-gaming-desktop-amd-ryzen-7-7700-16gb-memory-nvidia-geforce-rtx-3070-1tb-ssd-white/6533252.p?skuId=6533252',
            'https://www.bestbuy.com/site/ibuypower-tracemesh-gaming-desktop-intel-core-i7-13700f-16gb-memory-nvidia-geforce-rtx-3060-8gb-1tb-nvme-black/6536559.p?skuId=6536559',
            'https://www.bestbuy.com/site/cyberpowerpc-gamer-xtreme-gaming-desktop-intel-core-i7-13700f-16gb-memory-nvidia-geforce-rtx-3060-ti-1tb-ssd-black/6533257.p?skuId=6533257',
            'https://www.bestbuy.com/site/cyberpowerpc-gamer-master-gaming-desktop-amd-ryzen-7-7700-16gb-memory-nvidia-geforce-rtx-3060-ti-1tb-ssd-white/6533247.p?skuId=6533247',
            'https://www.bestbuy.com/site/hp-envy-2-in-1-14-full-hd-touch-screen-laptop-intel-core-i7-16gb-memory-1tb-ssd-natural-silver/6535747.p?skuId=6535747',
            'https://www.bestbuy.com/site/hp-15-6-touch-screen-laptop-intel-core-i7-16gb-memory-512gb-ssd-natural-silver/6477889.p?skuId=6477889',
            'https://www.bestbuy.com/site/hp-envy-2-in-1-15-6-full-hd-touch-screen-laptop-amd-ryzen-5-7530u-8gb-memory-256gb-ssd-nightfall-black/6535748.p?skuId=6535748',
            'https://www.bestbuy.com/site/lenovo-yoga-7i-16-wuxga-2-in-1-touch-screen-laptop-intel-core-i7-1355u-16gb-memory-512gb-ssd-storm-grey/6533950.p?skuId=6533950',
            'https://www.bestbuy.com/site/hp-14-chromebook-intel-celeron-4gb-memory-64gb-emmc-modern-gray/6513217.p?skuId=6513217',
            'https://www.bestbuy.com/site/lenovo-ideapad-3i-15-6-fhd-touch-laptop-core-i5-1135g7-with-8gb-memory-512gb-ssd-arctic-grey/6531744.p?skuId=6531744'
        ]
    },
    {
        'route': 'walmart',
        'urls': [
            'https://www.walmart.com/ip/Expert-Grill-Premium-Portable-Charcoal-Grill-Black-and-Stainless-Steel/731809852?athbdg=L1103',
            'https://www.walmart.com/ip/Blackstone-4-Burner-36-Griddle-Cooking-Station-with-Hard-Cover/1347629739?athbdg=L1200',
            'https://www.walmart.com/ip/Blackstone-2-Burner-28-Griddle-with-Air-Fryer-Combo/219229834?athbdg=L1102',
            'https://www.walmart.com/ip/Coleman-RoadTrip-X-Cursion-2-Burner-Propane-Gas-Portable-Grill/50093318?athbdg=L1102',
            'https://www.walmart.com/ip/Mainstays-Medium-3-Drawer-Plastic-Storage-Cart-with-Wheels-in-Classic-Mint/738193709',
            'https://www.walmart.com/ip/Acer-Chromebook-315-15-6-HD-Intel-Celeron-N4000-4GB-RAM-64GB-eMMC-Silver-CB315-3H-C19A/826255173?athbdg=L1600',
            'https://www.walmart.com/ip/Fantaslook-Womens-Tank-Tops-Summer-V-Neck-T-Shirts-Sleeveless-Tops-Side-Split-Tanks/2028341337?athbdg=L1600',
            'https://www.walmart.com/ip/Mainstays-Comfort-Complete-Bed-Pillow-Standard-Queen/744932389?athbdg=L1600',
            'https://www.walmart.com/ip/BIC-Brite-Liner-Highlighters-Chisel-Tip-Assorted-Colors-5-Count/13432804?athbdg=L1300',
            'https://www.walmart.com/ip/Tide-PODS-Laundry-Detergents-Spring-Meadow-112-Count/383607746?athbdg=L1600',
            'https://www.walmart.com/ip/onn-Wireless-Earphones-7-hours-playtime-Black/616108422?athbdg=L1600',
            'https://www.walmart.com/ip/Mainstays-Saucer-Chair-White-Faux-Shearling/3357732624',
            'https://www.walmart.com/ip/Mainstays-Mesh-Task-Chair-with-Plush-Padded-Seat-Multiple-Colors/213642741?athbdg=L1600',
            'https://www.walmart.com/ip/Fantaslook-Midi-Pleated-Skirts-for-Women-Polka-Dot-Swing-High-Waist-Maxi-Skirt-with-Pockets-Dresses/1550306237?athbdg=L1700',
            'https://www.walmart.com/ip/Lime-Crime-Unicorn-Hair-Semi-Permanent-Hair-Color-Vegan-Full-Coverage-Pony-6-76-fl-oz/943573109?athbdg=L1600'
        ]
    }
]

@pytest.mark.parametrize('store', stores)
def test_store(store):
    store_name = store['route']
    urls = store['urls']

    for url in urls:
        query_params = urlencode({'url': url})
        route = urljoin(f'/{store_name}', f'?{query_params}')

        # Update the route construction
        url_parts = urlsplit(route)
        route = url_parts.path + '?' + url_parts.query

        response = app.test_client().get(route)
        data = json.loads(response.data.decode('utf-8'))

        # Assertions
        if response.status_code == 400:
            print(url)
            time.sleep(3)
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert isinstance(data.get('name'), str)
        assert isinstance(data.get('price'), float)

