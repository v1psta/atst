from atst.app import make_config, make_app

config = make_config()
app = make_app(config)

if __name__ == "__main__":
    port = int(config["PORT"])
    app.run(port=port)
    print("Listening on http://localhost:%i" % port)
