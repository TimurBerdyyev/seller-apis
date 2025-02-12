# Описания файла `market.py`
Этот файл содержит скрипт для обновления информации о товарах на Яндекс.Маркете.
С помощью этого скрипта вы можете автоматически обновлять информацию о количестве товаров на складе и
их ценах на Яндекс.Маркете, чтобы ваш магазин всегда был актуален для покупателей.

## Основные возможности
1. Обновление остатков товаров: Скрипт автоматически загружает информацию о
количестве товаров на складе и обновляет эту информацию на Яндекс.Маркете.
2. Обновление цен на товары: Также скрипт обновляет цены на товары на
Яндекс.Маркете в соответствии с вашими текущими ценами.

## Как использовать
Чтобы использовать этот скрипт, вам нужно установить все необходимые переменные среды,
такие как токены доступа и идентификаторы кампаний и складов.
После этого вы можете запустить скрипт,
и он автоматически выполнит все необходимые операции по обновлению информации на Яндекс.Маркете.

## Примечания
* бедитесь, что все переменные среды установлены правильно перед запуском скрипта,
иначе он может не работать корректно.
* Этот скрипт предназначен для использования в автоматическом режиме
и не требует вмешательства пользователя после настройки переменных среды.

# Описания файла `seller.py`
Этот скрипт создан для обновления информации о товарах в вашем магазине на платформе Озон.
Он автоматически загружает данные о ценах и остатках товаров из внешнего источника и
обновляет соответствующие данные в вашем магазине на Озоне.

## Основные возможности
1. Обновление цен товаров: Скрипт загружает новые цены на товары из
внешнего источника и обновляет их в вашем магазине на Озоне.
2. Обновление остатков товаров:
Также скрипт загружает информацию об остатках товаров и обновляет ее в вашем магазине на Озоне.

## Использование файла `seller.py`
Перед использованием скрипта убедитесь, что у вас есть токены доступа к API Озона (SELLER_TOKEN и CLIENT_ID).
После этого запустите скрипт,
и он автоматически выполнит обновление информации о ценах и остатках товаров в вашем магазине на Озоне.