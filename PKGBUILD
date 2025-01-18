pkgname=chocolate-editor
pkgver=1.0.0
pkgrel=1
pkgdesc="A lightweight text editor built with Textual."
arch=('any')
url="https://github.com/chocolatefr/chocolate-editor"
license=('MIT')
depends=('python' 'python-pip')
source=("chocolate-editor.py"
        "style.css"
        "chocolate-editor"
        "requirements.txt")
sha256sums=('2b5b66fd34efbe5bf840200e9379cfa3aba1153aca78e1879d3071113023c62c'
            '2d1197de5acef5f65c0b7df626276a525359bd8696872c2ea526e63cc00eca46'
            'ef9205eb7d7dca575fed4f9a2112d30cab96f9cd35117e243c183a6e3418b864'
            '8c7399664b5f87a56ca51c0f790857da211e474520a7309c36c28ae8b49485c9')

package() {
    install -Dm755 chocolate-editor "$pkgdir/usr/bin/chocolate-editor"
    install -Dm644 chocolate-editor.py "$pkgdir/usr/share/$pkgname/chocolate-editor.py"
    install -Dm644 style.css "$pkgdir/usr/share/$pkgname/style.css"
    install -Dm644 requirements.txt "$pkgdir/usr/share/$pkgname/requirements.txt"

    # Install Python dependencies
    PYTHONUSERBASE="$pkgdir/usr/share/$pkgname" pip install --user -r requirements.txt
}
