# -*- coding:utf-8 -*-

from roller import app, scheduler

if __name__ == "__main__":
    print 'starting scheduler'
    app.run(debug=False, host="0.0.0.0", port=4444)
