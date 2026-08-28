import builtins
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .images import optimize_property_image
from .validators import validate_property_image


class Property(models.Model):
    class Purpose(models.TextChoices):
        SALE = "sale", "Venda"
        RENT = "rent", "Locação"

    class PropertyType(models.TextChoices):
        APARTMENT = "apartment", "Apartamento"
        HOUSE = "house", "Casa"
        PENTHOUSE = "penthouse", "Cobertura"
        LAND = "land", "Terreno"
        OFFICE = "office", "Sala comercial"
        STORE = "store", "Loja"
        BUILDING = "building", "Prédio"

    class Status(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicado"
        RESERVED = "reserved", "Reservado"
        SOLD = "sold", "Vendido"
        RENTED = "rented", "Alugado"
        ARCHIVED = "archived", "Arquivado"

    class AddressVisibility(models.TextChoices):
        FULL = "full", "Endereço completo"
        NEIGHBORHOOD_CITY = "neighborhood_city", "Bairro e cidade"

    class MapVisibility(models.TextChoices):
        HIDDEN = "hidden", "Mapa oculto"
        APPROXIMATE = "approximate", "Localização aproximada"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField("título", max_length=180)
    description = models.TextField("descrição")
    purpose = models.CharField("finalidade", max_length=8, choices=Purpose.choices)
    property_type = models.CharField(
        "tipo de imóvel", max_length=16, choices=PropertyType.choices
    )
    status = models.CharField(
        "situação", max_length=12, choices=Status.choices, default=Status.DRAFT
    )

    price = models.DecimalField("preço", max_digits=14, decimal_places=2)
    show_price = models.BooleanField("exibir preço", default=True)
    condominium_fee = models.DecimalField(
        "condomínio", max_digits=12, decimal_places=2, null=True, blank=True
    )
    total_area = models.DecimalField(
        "área total", max_digits=10, decimal_places=2
    )
    bedrooms = models.PositiveSmallIntegerField("quartos", null=True, blank=True)
    suites = models.PositiveSmallIntegerField("suítes", null=True, blank=True)
    bathrooms = models.PositiveSmallIntegerField(
        "banheiros", null=True, blank=True
    )
    parking_spaces = models.PositiveSmallIntegerField(
        "vagas de garagem", null=True, blank=True
    )

    street = models.CharField("logradouro", max_length=180)
    number = models.CharField("número", max_length=30)
    complement = models.CharField("complemento", max_length=100, blank=True)
    neighborhood = models.CharField("bairro", max_length=100)
    city = models.CharField("cidade", max_length=100)
    state = models.CharField("estado", max_length=2, default="RJ")
    postal_code = models.CharField("CEP", max_length=9, blank=True)
    address_visibility = models.CharField(
        "exibição do endereço",
        max_length=20,
        choices=AddressVisibility.choices,
        default=AddressVisibility.NEIGHBORHOOD_CITY,
    )

    exact_latitude = models.DecimalField(
        "latitude exata", max_digits=9, decimal_places=6, null=True, blank=True
    )
    exact_longitude = models.DecimalField(
        "longitude exata", max_digits=9, decimal_places=6, null=True, blank=True
    )
    public_latitude = models.DecimalField(
        "latitude aproximada", max_digits=9, decimal_places=6, null=True, blank=True
    )
    public_longitude = models.DecimalField(
        "longitude aproximada", max_digits=9, decimal_places=6, null=True, blank=True
    )
    map_visibility = models.CharField(
        "exibição do mapa",
        max_length=12,
        choices=MapVisibility.choices,
        default=MapVisibility.HIDDEN,
    )

    is_featured = models.BooleanField("destaque", default=False)
    featured_order = models.PositiveIntegerField(
        "ordem do destaque", null=True, blank=True
    )
    published_at = models.DateTimeField("publicado em", null=True, blank=True)
    archived_at = models.DateTimeField("arquivado em", null=True, blank=True)
    deleted_at = models.DateTimeField("enviado à lixeira em", null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        related_name="properties_created",
        on_delete=models.PROTECT,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="atualizado por",
        related_name="properties_updated",
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "imóvel"
        verbose_name_plural = "imóveis"
        ordering = ["-is_featured", "featured_order", "-created_at"]
        indexes = [
            models.Index(fields=["status", "deleted_at"]),
            models.Index(fields=["purpose", "property_type"]),
            models.Index(fields=["city", "neighborhood"]),
            models.Index(fields=["is_featured", "featured_order"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0), name="property_price_non_negative"
            ),
            models.CheckConstraint(
                condition=Q(condominium_fee__isnull=True)
                | Q(condominium_fee__gte=0),
                name="property_condominium_fee_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(total_area__gt=0), name="property_total_area_positive"
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def public_address(self):
        if self.address_visibility == self.AddressVisibility.FULL:
            parts = [self.street, self.number, self.complement, self.neighborhood, self.city]
            return ", ".join(part for part in parts if part)
        return f"{self.neighborhood}, {self.city}"

    def clean(self):
        errors = {}
        exact_coordinates = self.exact_latitude is not None and self.exact_longitude is not None
        partial_exact_coordinates = (self.exact_latitude is None) != (self.exact_longitude is None)
        public_coordinates = self.public_latitude is not None and self.public_longitude is not None
        partial_public_coordinates = (self.public_latitude is None) != (self.public_longitude is None)

        if partial_exact_coordinates:
            errors["exact_latitude"] = "Informe latitude e longitude exatas juntas."
        if partial_public_coordinates:
            errors["public_latitude"] = "Informe latitude e longitude públicas juntas."
        if self.map_visibility == self.MapVisibility.APPROXIMATE and not (
            exact_coordinates and public_coordinates
        ):
            errors["map_visibility"] = (
                "O mapa aproximado exige coordenadas exatas e públicas."
            )
        if self.is_featured and self.featured_order is None:
            errors["featured_order"] = "Defina a ordem do imóvel em destaque."
        if not self.is_featured:
            self.featured_order = None

        if errors:
            raise ValidationError(errors)

    def publication_errors(self):
        errors = []
        required_fields = {
            "title": "título",
            "description": "descrição",
            "purpose": "finalidade",
            "property_type": "tipo de imóvel",
            "price": "preço",
            "total_area": "área total",
            "street": "logradouro",
            "number": "número",
            "neighborhood": "bairro",
            "city": "cidade",
        }
        for field_name, label in required_fields.items():
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(label)

        if not self.pk or not self.images.exists():
            errors.append("pelo menos uma imagem")
        elif not self.images.filter(is_cover=True).exists():
            errors.append("uma imagem principal")
        if self.deleted_at is not None:
            errors.append("restauração do imóvel que está na lixeira")
        return errors


def property_image_path(instance, filename):
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    return f"properties/{instance.property.public_id}/{uuid.uuid4()}.{extension}"


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        verbose_name="imóvel",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        "imagem", upload_to=property_image_path, validators=[validate_property_image]
    )
    alt_text = models.CharField("texto alternativo", max_length=180, blank=True)
    order = models.PositiveSmallIntegerField("ordem", default=0)
    is_cover = models.BooleanField("foto principal", default=False)
    width = models.PositiveIntegerField("largura", null=True, editable=False)
    height = models.PositiveIntegerField("altura", null=True, editable=False)
    file_size = models.PositiveIntegerField("tamanho do arquivo", null=True, editable=False)
    image_format = models.CharField(
        "formato", max_length=12, blank=True, editable=False
    )
    created_at = models.DateTimeField("criada em", auto_now_add=True)

    class Meta:
        verbose_name = "imagem do imóvel"
        verbose_name_plural = "imagens dos imóveis"
        ordering = ["order", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["property", "order"], name="unique_property_image_order"
            ),
            models.UniqueConstraint(
                fields=["property"],
                condition=Q(is_cover=True),
                name="unique_property_cover_image",
            ),
        ]

    def __str__(self):
        return f"{self.property.title} — imagem {self.order + 1}"

    def clean(self):
        if self._state.adding and self.property_id:
            if self.property.images.count() >= 20:
                raise ValidationError("Cada imóvel pode ter no máximo 20 imagens.")

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            optimized, metadata = optimize_property_image(self.image.file)
            self.image.save(optimized.name, optimized, save=False)
            for field, value in metadata.items():
                setattr(self, field, value)
        super().save(*args, **kwargs)

    @builtins.property
    def thumbnail_url(self):
        if not self.image:
            return ""
        storage = self.image.storage
        if hasattr(storage, "transformed_url"):
            return storage.transformed_url(
                self.image.name, width=320, height=220, crop="fill"
            )
        return self.image.url


class PropertyChange(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Criado"
        UPDATED = "updated", "Atualizado"
        STATUS_CHANGED = "status_changed", "Situação alterada"
        TRASHED = "trashed", "Enviado à lixeira"
        RESTORED = "restored", "Restaurado"
        DELETED = "deleted", "Excluído definitivamente"

    property = models.ForeignKey(
        Property,
        verbose_name="imóvel",
        related_name="changes",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    property_title = models.CharField("título do imóvel", max_length=180)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="responsável",
        related_name="property_changes",
        null=True,
        on_delete=models.SET_NULL,
    )
    action = models.CharField("ação", max_length=20, choices=Action.choices)
    changes = models.JSONField("alterações", default=dict, blank=True)
    created_at = models.DateTimeField("realizada em", auto_now_add=True)

    class Meta:
        verbose_name = "alteração do imóvel"
        verbose_name_plural = "alterações dos imóveis"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_display()} — {self.property_title}"
