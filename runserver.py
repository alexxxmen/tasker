# -*- coding:utf-8 -*-

from roller import app

if __name__ == "__main__":
    print 'starting scheduler'
    app.run(debug=True, host="0.0.0.0", port=4444)
