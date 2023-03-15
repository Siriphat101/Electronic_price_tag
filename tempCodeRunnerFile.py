sql = """SELECT product_id FROM devices WHERE chipID = '{}'""".format(chipID)
                            # cur.execute(sql)
                            # product_id = cur.fetchone()
                            
                            # # get product name and price
                            # sql = """SELECT product_name,product_price FROM product WHERE product_id = '{}'""".format(product_id)
                            # cur.execute(sql)
                            # product = cur.fetchone()
                            # product_name = product[0]
                            # product_price = product[1]
                            
                            # print(product_id, product_name, product_price)
                            # data_json = {
                            #     "mode": "single",
                            #     "chip_id": chipID,
                            #     "msg": [
                            #         product_name, product_price,

                            #     ],
                            #     "timestamp": ts
                            # }

                            # mqtt_client.publish("/pricetagProjectNPU",
                            #                     json.dumps(data_json), qos=1)